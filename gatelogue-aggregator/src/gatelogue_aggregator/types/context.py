from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Self, override, cast

import msgspec
import networkx as nx
import pygraphviz

if TYPE_CHECKING:
    from collections.abc import Iterable

import rich
import rich.progress

from gatelogue_aggregator.types.air import AirContext, AirSource, Flight, Airport, Airline, Gate
from gatelogue_aggregator.types.base import Node, ToSerializable


class Context(AirContext, ToSerializable):
    @classmethod
    def from_sources(cls, sources: Iterable[AirSource]) -> Self:
        self = cls()
        for source in rich.progress.track(sources, f"[yellow]Merging sources: {', '.join(s.name for s in sources)}"):
            self.g = nx.compose(self.g, source.g)

        processed: dict[type[Node], dict[str, list[Node]]] = {}
        to_merge = []
        for n in rich.progress.track(self.g.nodes, "[green]  Finding equivalent nodes"):
            key = n.key(self)
            ty = type(n)
            filtered_processed = processed.get(ty, {}).get(key, [])
            if (equiv := next((a for a in filtered_processed if n.equivalent(self, a)), None)) is None:
                processed.setdefault(ty, {}).setdefault(key, []).append(n)
                continue
            to_merge.append((equiv, n))
        for equiv, n in rich.progress.track(to_merge, "[green]  Merging equivalent nodes"):
            equiv.merge(self, n)
        self.update()
        return self

    def update(self):
        AirContext.update(self)

    @override
    class Ser(AirContext.Ser):
        timestamp: str = msgspec.field(default_factory=lambda: datetime.datetime.now().strftime("%Y%m%d-%H%M%S%Z"))  # noqa: DTZ005

    def ser(self) -> Context.Ser:
        air = AirContext.ser(self)
        return self.Ser(
            flight=air.flight,
            airport=air.airport,
            gate=air.gate,
            airline=air.airline,
        )

    def graph(self, path: Path):
        g = cast(nx.MultiGraph, self.g.copy())
        for node in g.nodes:
            g.nodes[node]["style"] = "filled"
            for ty, col in ((Flight, "#ff8080"), (Airport, "#8080ff"), (Airline, "#ffff80"), (Gate, "#80ff80")):
                if isinstance(node, ty):
                    g.nodes[node]["fillcolor"] = col
                    break
        for u, v, k in g.edges:
            for ty1, ty2, col in [(Airport, Gate, "#0000ff"), (Gate, Flight, "#00ff00"), (Flight, Airline, "#ff0000")]:
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
