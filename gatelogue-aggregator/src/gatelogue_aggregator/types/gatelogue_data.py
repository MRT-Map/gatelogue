from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

import rich

import gatelogue_types as gt
import rustworkx as rx
from rustworkx.visualization.graphviz import graphviz_draw

from gatelogue_aggregator.logging import INFO1, INFO2, track
from gatelogue_aggregator.types.edge.proximity import ProximitySource
from gatelogue_aggregator.types.edge.shared_facility import SharedFacility, SharedFacilitySource
from gatelogue_aggregator.types.node.air import AirAirline, AirAirport, AirFlight, AirGate, AirSource
from gatelogue_aggregator.types.node.base import Node
from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusSource, BusStop
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailSource, RailStation
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaSource, SeaStop
from gatelogue_aggregator.types.node.spawn_warp import SpawnWarp, SpawnWarpSource
from gatelogue_aggregator.types.node.town import Town, TownSource
from gatelogue_aggregator.types.source import Sourced

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class GatelogueData(
    AirSource, RailSource, SeaSource, BusSource, TownSource, SpawnWarpSource, ProximitySource, SharedFacilitySource
):
    name = "Gatelogue"
    priority = 0

    @classmethod
    def from_sources(cls, sources: Iterable[AirSource | RailSource | SeaSource | BusSource | TownSource]) -> Self:
        self = cls.__new__(cls)
        self.g = rx.PyGraph()

        for source in track(sources, description=INFO1 + "Merging sources", remove=False):
            source.sanitise_strings()
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

        edges: dict[tuple[float, float], list[Sourced[Any]]] = {}
        for i in track(self.g.edge_indices(), description=INFO2 + "Merging edges", remove=False):
            u, v = self.g.get_edge_endpoints_by_index(i)
            k = self.g.get_edge_data_by_index(i)

            edge_list = edges.setdefault((u, v), [])
            if (existing := next((a for a in edge_list if a.v == k.v), None)) is not None:
                existing.source(k)
                self.g.remove_edge_from_index(i)
            else:
                edge_list.append(k)

        self.update()
        return self

    def update(self):
        AirSource.update(self)
        ProximitySource.update(self)
        SharedFacilitySource.update(self)

    def report(self):
        rich.print(INFO1 + "Below is a final report of all nodes collected")
        for node in self.g.nodes():
            node.report(self)
        rich.print(INFO1 + "End of report")

    def export(self) -> gt.GatelogueData:
        return gt.GatelogueData(
            nodes={a.i: a.export(self) for a in track(self.g.nodes(), description=INFO2 + "Exporting", remove=False)}
        )

    def graph(self, path: Path):
        g = self.g.copy()
        for i, (u, v, data) in g.edge_index_map().items():
            g.update_edge_by_index(i, (u, v, data))

        def replace(s):
            return s.replace('"', '\\"')

        def node_fn(node: Node):
            d = {
                "style": "filled",
                "tooltip": replace(Node.str_src(node, self)),
                "label": replace(node.str_src(self)),
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
                (SpawnWarp, "#aaaaaa"),
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
                d["tooltip"] = replace(f"({u.str_src(self)} -- {v.str_src(self)})")
            else:
                d["tooltip"] = replace(f"{edge_data} ({u.str_src(self)} -- {v.str_src(self)})")
            if isinstance(edge_data, gt.Proximity):
                d["color"] = '"#ff00ff"'
                return d
            if isinstance(edge_data, SharedFacility):
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
