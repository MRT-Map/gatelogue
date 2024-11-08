from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Self, cast, override

import msgspec
import rustworkx as rx
from rustworkx.visualization.graphviz import graphviz_draw

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.logging import INFO1, INFO2, track
from gatelogue_aggregator.types.base import Sourced
from gatelogue_aggregator.types.node.bus import BusCompany, BusContext, BusLine, BusSource, BusStop
from gatelogue_aggregator.types.node.rail import RailCompany, RailContext, RailLine, RailSource, RailStation
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaContext, SeaLine, SeaSource, SeaStop
from gatelogue_aggregator.types.node.town import Town, TownContext, TownSource

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    import pygraphviz


from gatelogue_aggregator.types.connections import Proximity
from gatelogue_aggregator.types.node.air import AirAirline, AirAirport, AirContext, AirFlight, AirGate, AirSource
from gatelogue_aggregator.types.node.base import LocatedNode, Node


class Context(AirContext, RailContext, SeaContext, BusContext, TownContext):
    @classmethod
    def from_sources(cls, sources: Iterable[AirSource | RailSource | SeaSource | BusSource | TownSource]) -> Self:
        self = cls()
        for source in track(sources, description=INFO1 + "Merging sources", remove=False):
            self.g = rx.graph_union(self.g, source.g)

        processed: dict[type[Node], dict[str, list[Node]]] = {}
        to_merge = []
        for n in track(self.g.nodes(), description=INFO2 + "Finding equivalent nodes", nonlinear=True, remove=False):
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
        AirContext.update(self)

        processed = []
        for node in track(self.g.nodes(), description=INFO1 + "Linking close nodes", nonlinear=True, remove=False):
            if not isinstance(node, LocatedNode) or node.coordinates is None:
                continue
            node_coordinates = node.coordinates.v
            if node.world is None:
                continue
            for existing, existing_world, existing_coordinates in processed:
                if existing_world != node.world.v:
                    continue
                x1, y1 = existing_coordinates
                x2, y2 = node_coordinates
                dist = (x1 - x2) ** 2 + (y1 - y2) ** 2
                threshold = 500 if isinstance(existing, AirAirport) or isinstance(node, AirAirport) else 250
                if dist < threshold**2:
                    node.connect(self, existing, value=Proximity(dist**0.5))
            processed.append((node, node.world.v, node_coordinates))

    @override
    class Export(msgspec.Struct, kw_only=True):
        nodes: list[Node]
        """List of all nodes, along with their connections to other nodes"""
        timestamp: str = msgspec.field(default_factory=lambda: datetime.datetime.now().isoformat())  # noqa: DTZ005
        """Time that the aggregation of the data was done"""
        version: int = int(__version__.split("+")[1])
        """Version number of the database format"""

    def export(self, _=None) -> Context.Ser:
        for node in self.g.nodes():
            node.prepare_export(self)
        return self.Export(self.g.nodes())

    def graph(self, path: Path):
        # g = cast(rx.PyGraph, self.g.copy())
        # for node in g.nodes:
        #     g.nodes[node]["style"] = "filled"
        #     g.nodes[node]["tooltip"] = Node.str_ctx(node, self)
        #     for ty, col in (
        #         (AirFlight, "#ff8080"),
        #         (AirAirport, "#8080ff"),
        #         (AirAirline, "#ffff80"),
        #         (AirGate, "#80ff80"),
        #         (RailCompany, "#ffff80"),
        #         (RailLine, "#ff8080"),
        #         (RailStation, "#8080ff"),
        #         (SeaCompany, "#ffff80"),
        #         (SeaLine, "#ff8080"),
        #         (SeaStop, "#8080ff"),
        #         (BusCompany, "#ffff80"),
        #         (BusLine, "#ff8080"),
        #         (BusStop, "#8080ff"),
        #         (Town, "#aaaaaa"),
        #     ):
        #         if isinstance(node, ty):
        #             g.nodes[node]["fillcolor"] = col
        #             break
        # for u, v, k in g.edges:
        #     edge_data = g.edges[u, v, k]["v"]
        #     if edge_data is not None:
        #         g.edges[u, v, k]["tooltip"] = f"{edge_data} ({u.str_ctx(self)} -- {v.str_ctx(self)})"
        #     if isinstance(edge_data, Proximity):
        #         g.edges[u, v, k]["color"] = "#ff00ff"
        #         continue
        #     for ty1, ty2, col in (
        #         (AirAirport, AirGate, "#0000ff"),
        #         (AirGate, AirFlight, "#00ff00"),
        #         (AirFlight, AirAirline, "#ff0000"),
        #         (RailCompany, RailLine, "#ff0000"),
        #         (RailStation, RailStation, "#0000ff"),
        #         (SeaCompany, SeaLine, "#ff0000"),
        #         (SeaStop, SeaStop, "#0000ff"),
        #         (BusCompany, BusLine, "#ff0000"),
        #         (BusStop, BusStop, "#0000ff"),
        #     ):
        #         if (isinstance(u, ty1) and isinstance(v, ty2)) or (isinstance(u, ty2) and isinstance(v, ty1)):
        #             g.edges[u, v, k]["color"] = col
        #             break
        #     else:
        #         g.edges[u, v, k]["style"] = "invis"
        #
        # g: rx.PyGraph = nx.relabel_nodes(g, {n: n.str_ctx(self) for n in g.nodes})
        #
        # g: pygraphviz.AGraph = nx.drawing.nx_agraph.to_agraph(g)
        # g.graph_attr["overlap"] = "prism1000"
        # g.graph_attr["outputorder"] = "edgesfirst"
        # g.draw(path, prog="sfdp", args="")
        def node_fn(node: Node):
            d = dict(
                style="filled",
                tooltip=Node.str_ctx(node, self),
                label=Node.str_ctx(node, self),
            )
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
                    d["fillcolor"] = col
                    break
            return d

        def edge_fn(edge):
            edge_data = edge.v if isinstance(edge, Sourced) else edge
            d = {}
            if edge_data is not None:
                d["tooltip"] = f"{edge_data} ({u.str_ctx(self)} -- {v.str_ctx(self)})"
            if isinstance(edge_data, Proximity):
                d["color"] = "#ff00ff"
                return d
            # for ty1, ty2, col in (
            #     (AirAirport, AirGate, "#0000ff"),
            #     (AirGate, AirFlight, "#00ff00"),
            #     (AirFlight, AirAirline, "#ff0000"),
            #     (RailCompany, RailLine, "#ff0000"),
            #     (RailStation, RailStation, "#0000ff"),
            #     (SeaCompany, SeaLine, "#ff0000"),
            #     (SeaStop, SeaStop, "#0000ff"),
            #     (BusCompany, BusLine, "#ff0000"),
            #     (BusStop, BusStop, "#0000ff"),
            # ):
            #     self.g.edge
            #     if (isinstance(u, ty1) and isinstance(v, ty2)) or (isinstance(u, ty2) and isinstance(v, ty1)):
            #         d["color"] = col
            #         break
            # else:
            #     d["style"] = "invis"
            return d

        graphviz_draw(
            self.g,
            node_attr_fn=node_fn,
            edge_attr_fn=edge_fn,
            graph_attr=dict(overlap="prism1000", outputorder="edgesfirst"),
            filename=path,
            method="sfdp",
        )
