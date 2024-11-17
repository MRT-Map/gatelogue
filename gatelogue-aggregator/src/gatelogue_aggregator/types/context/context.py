from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Self, override

import msgspec
import rustworkx as rx
from rustworkx.visualization.graphviz import graphviz_draw

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.logging import INFO1, INFO2, track
from gatelogue_aggregator.types.context.shared_facility import SharedFacilityContext, SharedFacility
from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusSource, BusStop
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailSource, RailStation
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaSource, SeaStop
from gatelogue_aggregator.types.node.town import Town, TownSource
from gatelogue_aggregator.types.source import Sourced

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.node.air import AirAirline, AirAirport, AirFlight, AirGate, AirSource
from gatelogue_aggregator.types.node.base import Node
from gatelogue_aggregator.types.context.proximity import Proximity, ProximityContext


class Context(AirSource, RailSource, SeaSource, BusSource, TownSource, ProximityContext, SharedFacilityContext):
    @classmethod
    def from_sources(cls, sources: Iterable[AirSource | RailSource | SeaSource | BusSource | TownSource]) -> Self:
        self = cls()
        for source in track(sources, description=INFO1 + "Merging sources", remove=False):
            source.prepare_merge(self.g)
            self.g = rx.graph_union(self.g, source.g)

        processed: dict[type[Node], dict[str, list[Node]]] = {}
        to_merge: list[tuple[Node, Node]] = []
        for i in track(
            self.g.node_indices(), description=INFO2 + "Finding equivalent nodes", nonlinear=True, remove=False
        ):
            n = self.g[i]
            n.i = i
            key = n.merge_key(self)
            ty = type(n)
            filtered_processed = processed.get(ty, {}).get(key, [])
            if (equiv := next((a for a in filtered_processed if n.equivalent(self, a)), None)) is None:
                processed.setdefault(ty, {}).setdefault(key, []).append(n)
                continue
            to_merge.append((equiv, n))
        for equiv, n in track(to_merge, description=INFO2 + "Merging equivalent nodes", remove=False):
            equiv.merge(self, n)
        self.update()
        return self

    def update(self):
        AirSource.update(self)
        ProximityContext.update(self)
        SharedFacilityContext.update(self)

    @override
    class Export(msgspec.Struct, kw_only=True):
        nodes: dict[int, Node]
        """List of all nodes, along with their connections to other nodes"""
        timestamp: str = msgspec.field(default_factory=lambda: datetime.datetime.now().isoformat())  # noqa: DTZ005
        """Time that the aggregation of the data was done"""
        version: int = int(__version__.split("+")[1])
        """Version number of the database format"""

    def export(self) -> Context.Export:
        for node in track(self.g.nodes(), description=INFO2 + "Preparing nodes for export", remove=False):
            node.prepare_export(self)
        for edge in track(self.g.edges(), description=INFO2 + "Preparing edges for export", remove=False):
            if isinstance(edge.v, Connection):
                edge.v.prepare_export(self)
        return self.Export(nodes={a.i: a for a in self.g.nodes()})

    def graph(self, path: Path):
        g = self.g.copy()
        for i, (u, v, data) in g.edge_index_map().items():
            g.update_edge_by_index(i, (u, v, data))

        def replace(s):
            return s.replace('"', '\\"')

        def node_fn(node: Node):
            d = {
                "style": "filled",
                "tooltip": replace(Node.str_ctx(node, self)),
                "label": replace(node.str_ctx(self)),
            }
            for ty, col in (
                (AirFlight, "#ff8080"),
                (AirAirport, "#8080ff"),
                (AirAirline, "#ffff80"),
                (AirGate, "#80ff80"),
                (RailCompany, "#ffff80"),
                (RailLine, "#ff8080"),
                (RailStation, "#8080ff"),
                (SeaCompany, "#ffff80"),
                (SeaLine, "#ff8080"),
                (SeaStop, "#8080ff"),
                (BusCompany, "#ffff80"),
                (BusLine, "#ff8080"),
                (BusStop, "#8080ff"),
                (Town, "#aaaaaa"),
            ):
                if isinstance(node, ty):
                    d["fillcolor"] = '"' + col + '"'
                    break
            return d

        def edge_fn(edge):
            u = g[edge[0]]
            v = g[edge[1]]
            edge = edge[2]
            edge_data = edge.v if isinstance(edge, Sourced) else edge
            d = {}
            if edge_data is None:
                d["tooltip"] = replace(f"({u.str_ctx(self)} -- {v.str_ctx(self)})")
            else:
                d["tooltip"] = replace(f"{edge_data} ({u.str_ctx(self)} -- {v.str_ctx(self)})")
            if isinstance(edge_data, Proximity):
                d["color"] = '"#ff00ff"'
                return d
            elif isinstance(edge_data, SharedFacility):
                d["color"] = '"#008080"'
                return d
            for ty1, ty2, col in (
                (AirAirport, AirGate, "#0000ff"),
                (AirGate, AirFlight, "#00ff00"),
                (AirFlight, AirAirline, "#ff0000"),
                (RailCompany, RailLine, "#ff0000"),
                (RailStation, RailStation, "#0000ff"),
                (SeaCompany, SeaLine, "#ff0000"),
                (SeaStop, SeaStop, "#0000ff"),
                (BusCompany, BusLine, "#ff0000"),
                (BusStop, BusStop, "#0000ff"),
            ):
                if (isinstance(u, ty1) and isinstance(v, ty2)) or (isinstance(u, ty2) and isinstance(v, ty1)):
                    d["color"] = '"' + col + '"'
                    break
            else:
                d["style"] = "invis"
            return d

        # g.to_dot(
        #     node_attr=node_fn,
        #     edge_attr=edge_fn,
        #     graph_attr={"overlap": "prism1000", "outputorder": "edgesfirst"}, filename="test.dot")
        graphviz_draw(
            g,
            node_attr_fn=node_fn,
            edge_attr_fn=edge_fn,
            graph_attr={"overlap": "prism1000", "outputorder": "edgesfirst"},
            filename=str(path),
            image_type="svg",
            method="sfdp",
        )
