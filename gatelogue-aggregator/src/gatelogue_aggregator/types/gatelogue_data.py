from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Self

import gatelogue_types as gt
import rich
import rustworkx as rx
from rustworkx.visualization.graphviz import graphviz_draw

from gatelogue_aggregator.logging import INFO1, INFO2, RESULT, track, progress_bar
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.edge.proximity import ProximitySource
from gatelogue_aggregator.types.edge.shared_facility import SharedFacility, SharedFacilitySource
from gatelogue_aggregator.types.node._air import AirAirline, AirAirport, AirFlight, AirGate, AirSource
from gatelogue_aggregator.types.node.base import Node
from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusSource, BusStop
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailSource, RailStation
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaSource, SeaStop
from gatelogue_aggregator.types.node.spawn_warp import SpawnWarp, SpawnWarpSource
from gatelogue_aggregator.types.node.town import Town, TownSource
from gatelogue_aggregator.types.source import Source

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class GatelogueData:
    def __init__(self, config: Config, sources: Iterable[type[Source]], database=":memory:"):
        self.config = config
        for i, source in enumerate(sources):
            source.priority = i
        self.gd = gt.GD.create([a.__name__ for a in sources], database)

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            list(executor.map(lambda s: s(self.config, self.gd.conn), sources))

        prev_length: int | None = None

        for pass_ in range(1, 10):
            # processed: dict[type[Node], dict[str | None, list[Node]]] = {}
            # to_merge: list[tuple[Node, Node]] = []
            merged: set[int] = set()
            for n in track(
                self.gd.nodes(),
                INFO2,
                description=f"Merging equivalent nodes (pass {pass_})",
            ):
                if n.i in merged:
                    continue
                for equiv in n.equivalent_nodes():
                    n.merge(equiv)
                    merged.add(equiv.i)

            for n in track(
                self.gd.nodes(gt.AirAirport),
                INFO2,
                description=f"Merging airports (pass {pass_})",
            ):
                if not n.code.startswith("NOCODE"):
                    continue
                if (equiv := n.find_equiv_from_name(self)) is not None:
                    rich.print(
                        RESULT
                        + f"AirAirport of name `{n.names}` found code `{equiv.code}` with similar name `{equiv.names}`"
                    )
                    n.code = equiv.code
                    equiv.merge(n)

            if len(self.gd) == prev_length:
                break
            prev_length = len(self.gd)

        AirSource.update(self)
        ProximitySource.update(self)
        SharedFacilitySource.update(self)

    def report(self):
        rich.print(INFO1 + "Below is a final report of all nodes collected")
        for node in self.gd.nodes():
            node.report(self)
        rich.print(INFO1 + "End of report")

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
