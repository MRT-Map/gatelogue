from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Self, cast, override

import msgspec
import networkx as nx

from gatelogue_aggregator.logging import INFO1, INFO2, track
from gatelogue_aggregator.types.node.rail import RailCompany, RailContext, RailLine, RailSource, Station
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaContext, SeaLine, SeaSource, SeaStop

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    import pygraphviz


from gatelogue_aggregator.types.base import ToSerializable
from gatelogue_aggregator.types.connections import Proximity
from gatelogue_aggregator.types.node.air import AirContext, Airline, Airport, AirSource, Flight, Gate
from gatelogue_aggregator.types.node.base import LocatedNode, Node


class Context(AirContext, RailContext, SeaContext, ToSerializable):
    @classmethod
    def from_sources(cls, sources: Iterable[AirSource | RailSource | SeaSource]) -> Self:
        self = cls()
        for source in track(sources, description=INFO1 + "Merging sources", remove=False):
            self.g = nx.compose(self.g, source.g)

        processed: dict[type[Node], dict[str, list[Node]]] = {}
        to_merge = []
        for n in track(self.g.nodes, description=INFO2 + "Finding equivalent nodes", nonlinear=True, remove=False):
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
        for node in track(self.g.nodes, description=INFO1 + "Linking close nodes", nonlinear=True, remove=False):
            if not isinstance(node, LocatedNode) or (node_coordinates := node.merged_attr(self, "coordinates")) is None:
                continue
            node_coordinates = node_coordinates.v
            if (node_world := node.merged_attr(self, "world")) is None:
                continue
            for existing, existing_world, existing_coordinates in processed:
                if existing_world != node_world.v:
                    continue
                x1, y1 = existing_coordinates
                x2, y2 = node_coordinates
                dist = (x1 - x2) ** 2 + (y1 - y2) ** 2
                threshold = 500 if isinstance(existing, Airport) or isinstance(node, Airport) else 250
                if dist < threshold**2:
                    node.connect(self, existing, value=Proximity(dist**0.5))
            processed.append((node, node_world.v, node_coordinates))

    @override
    class Ser(msgspec.Struct, kw_only=True):
        air: AirContext.Ser
        rail: RailContext.Ser
        sea: SeaContext.Ser
        timestamp: str = msgspec.field(default_factory=lambda: datetime.datetime.now().strftime("%Y%m%d-%H%M%S%Z"))  # noqa: DTZ005
        version: int = 1

    def ser(self, _=None) -> Context.Ser:
        return self.Ser(air=AirContext.ser(self), rail=RailContext.ser(self), sea=SeaContext.ser(self))

    def graph(self, path: Path):
        g = cast(nx.MultiGraph, self.g.copy())
        for node in g.nodes:
            g.nodes[node]["style"] = "filled"
            g.nodes[node]["tooltip"] = Node.str_ctx(node, self)
            for ty, col in (
                (Flight, "#ff8080"),
                (Airport, "#8080ff"),
                (Airline, "#ffff80"),
                (Gate, "#80ff80"),
                (RailCompany, "#ffff80"),
                (RailLine, "#ff8080"),
                (Station, "#8080ff"),
                (SeaCompany, "#ffff80"),
                (SeaLine, "#ff8080"),
                (SeaStop, "#8080ff"),
            ):
                if isinstance(node, ty):
                    g.nodes[node]["fillcolor"] = col
                    break
        for u, v, k in g.edges:
            edge_data = g.edges[u, v, k]["v"]
            if edge_data is not None:
                g.edges[u, v, k]["tooltip"] = f"{edge_data} ({u.str_ctx(self)} -- {v.str_ctx(self)})"
            if isinstance(edge_data, Proximity):
                g.edges[u, v, k]["color"] = "#ff00ff"
                continue
            for ty1, ty2, col in (
                (Airport, Gate, "#0000ff"),
                (Gate, Flight, "#00ff00"),
                (Flight, Airline, "#ff0000"),
                (RailCompany, RailLine, "#ff0000"),
                (Station, Station, "#0000ff"),
                (SeaCompany, SeaLine, "#ff0000"),
                (SeaStop, SeaStop, "#0000ff"),
            ):
                if (isinstance(u, ty1) and isinstance(v, ty2)) or (isinstance(u, ty2) and isinstance(v, ty1)):
                    g.edges[u, v, k]["color"] = col
                    break
            else:
                g.edges[u, v, k]["style"] = "invis"

        g: nx.MultiGraph = nx.relabel_nodes(g, {n: n.str_ctx(self) for n in g.nodes})

        g: pygraphviz.AGraph = nx.drawing.nx_agraph.to_agraph(g)
        g.graph_attr["overlap"] = "prism1000"
        g.graph_attr["outputorder"] = "edgesfirst"
        g.draw(path, prog="sfdp", args="")
