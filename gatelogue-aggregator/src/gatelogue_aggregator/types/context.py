from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

import networkx as nx

if TYPE_CHECKING:
    from collections.abc import Iterable

import rich
import rich.progress

from gatelogue_aggregator.types.air import AirContext, AirSource
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
        pass

    def ser(self) -> Context.Ser:
        air = AirContext.ser(self)
        return self.Ser(
            flight=air.flight,
            airport=air.airport,
            gate=air.gate,
            airline=air.airline,
        )
