from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from collections.abc import Iterable

import rich
import rich.progress

from gatelogue_aggregator.types.air import Airline, Airport, Flight, Gate
from gatelogue_aggregator.types.base import MergeableObject, Source


class AirContext:
    __slots__ = ("flight", "airport", "gate", "airline")
    flight: list[Flight]
    airport: list[Airport]
    gate: list[Gate]
    airline: list[Airline]

    def __init__(self):
        self.flight = []
        self.airport = []
        self.gate = []
        self.airline = []

    def get_flight(self, **query) -> Flight:
        for o in self.flight:
            if all(v == getattr(o, k) for k, v in query.items()):
                return o
        o = Flight(**query)
        o.ctx(self)
        return o

    def get_airport(self, **query) -> Airport:
        for o in self.airport:
            if all(v == getattr(o, k) for k, v in query.items()):
                return o
        o = Airport(**query)
        o.ctx(self)
        return o

    def get_gate(self, **query) -> Gate:
        for o in self.gate:
            if all(v == getattr(o, k) for k, v in query.items()):
                return o
        o = Gate(**query)
        o.ctx(self)
        return o

    def get_airline(self, **query) -> Airline:
        for o in self.airline:
            if all(v == getattr(o, k) for k, v in query.items()):
                return o
        o = Airline(**query)
        o.ctx(self)
        return o

    def update(self):
        for o in self.flight:
            o.update()
        for o in self.airport:
            o.update()
        for o in self.gate:
            o.update()
        for o in self.airline:
            o.update()

    def dict(self) -> dict[str, dict[str, Any]]:
        return {
            "flight": {str(o.id): o.dict() for o in self.flight},
            "airport": {str(o.id): o.dict() for o in self.airport},
            "gate": {str(o.id): o.dict() for o in self.gate},
            "airline": {str(o.id): o.dict() for o in self.airline},
        }


class Context(AirContext):
    @classmethod
    def from_sources(cls, sources: Iterable[Source]) -> Self:
        self = cls()
        rich.print("[yellow] Merging sources")
        for source in rich.progress.track(sources, f"[yellow] Merging sources: {', '.join(s.name for s in sources)}"):
            if isinstance(source, AirContext):
                MergeableObject.merge_lists(self.flight, source.flight)
                MergeableObject.merge_lists(self.airport, source.airport)
                MergeableObject.merge_lists(self.gate, source.gate)
                MergeableObject.merge_lists(self.airline, source.airline)
        return self

    def update(self):
        AirContext.update(self)

    def dict(self) -> dict[str, dict[str, Any]]:
        return AirContext.dict(self)
