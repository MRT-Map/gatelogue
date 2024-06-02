from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

import networkx as nx

if TYPE_CHECKING:
    from collections.abc import Iterable

import rich
import rich.progress

from gatelogue_aggregator.types.air import AirContext, Airline, Airport, Flight, Gate
from gatelogue_aggregator.types.base import BaseContext, Source, ToSerializable


class Context(AirContext, ToSerializable):
    @classmethod
    def from_sources(cls, sources: Iterable[BaseContext | Source]) -> Self:
        self = cls()
        for source in rich.progress.track(sources, f"[yellow]Merging sources: {', '.join(s.name for s in sources)}"):
            self.g = nx.compose(self.g, source.g)
        for ty in (Flight, Airport, Airline, Gate):
            processed = []
            for n in self.g.nodes:
                if not isinstance(n, ty):
                    continue
                if (equiv := next((a for a in processed if n.equivalent(self, a)), None)) is None:
                    processed.append(n)
                    continue
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
