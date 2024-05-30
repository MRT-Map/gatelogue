from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self, override

import msgspec

from gatelogue_aggregator.types.base import IdObject, MergeableObject, Sourced

if TYPE_CHECKING:
    from gatelogue_aggregator.types.context import AirContext


class Flight(IdObject, kw_only=True):
    codes: set[str]
    gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)
    airline: Sourced[Airline]

    @override
    def ctx(self, ctx: AirContext):
        ctx.flight.append(self)

    @override
    def update(self):
        for gate in self.gates:
            if self not in (o.v for o in gate.v.flights):
                gate.v.flights.append(self.source(gate))
        if self not in (o.v for o in self.airline.v.flights):
            self.airline.v.flights.append(self.source(self.airline))

    def equivalent(self, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.airline.equivalent(other.airline)

    def merge(self, other: Self):
        if other.id != self.id:
            other.id.id = self.id
        else:
            return
        self.codes.update(other.codes)
        MergeableObject.merge_lists(self.gates, other.gates)
        self.airline.merge(other.airline)

    def dict(self) -> dict[str, Any]:
        return {"codes": self.codes, "gates": [o.dict() for o in self.gates], "airline": self.airline.dict()}


class Airport(IdObject, kw_only=True):
    code: str
    coordinates: Sourced[tuple[int, int]] | None = None
    gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)

    @override
    def ctx(self, ctx: AirContext):
        ctx.airport.append(self)

    @override
    def update(self):
        for gate in self.gates:
            gate.v.airport = self.source(gate)

    def equivalent(self, other: Self) -> bool:
        return self.code == other.code

    def merge(self, other: Self):
        if other.id != self.id:
            other.id.id = self.id
        else:
            return
        self.coordinates = self.coordinates or other.coordinates
        MergeableObject.merge_lists(self.gates, other.gates)

    def dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "coordinates": self.coordinates.dict() if self.coordinates is not None else None,
            "gates": [o.dict() for o in self.gates],
        }


class Gate(IdObject, kw_only=True):
    code: str | None
    flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)
    airport: Sourced[Airport]
    size: Sourced[str] | None = None

    @override
    def ctx(self, ctx: AirContext):
        ctx.gate.append(self)

    @override
    def update(self):
        for flight in self.flights:
            if self not in (o.v for o in flight.v.gates):
                flight.v.gates.append(self.source(flight))
        if self not in (o.v for o in self.airport.v.gates):
            self.airport.v.gates.append(self.source(self.airport))

    def equivalent(self, other: Self) -> bool:
        return self.code == other.code and self.airport.equivalent(other.airport)

    def merge(self, other: Self):
        if other.id != self.id:
            other.id.id = self.id
        else:
            return
        self.size = self.size or other.size
        MergeableObject.merge_lists(self.flights, other.flights)
        self.airport.merge(other.airport)

    def dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "flights": [o.dict() for o in self.flights],
            "airport": self.airport.dict(),
            "size": self.size.dict() if self.size is not None else None,
        }


class Airline(IdObject, kw_only=True):
    name: str
    flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)

    @override
    def ctx(self, ctx: AirContext):
        ctx.airline.append(self)

    @override
    def update(self):
        for flight in self.flights:
            flight.v.airline = self.source(flight)

    def equivalent(self, other: Self) -> bool:
        return self.name == other.name

    def merge(self, other: Self):
        if other.id != self.id:
            other.id.id = self.id
        else:
            return
        MergeableObject.merge_lists(self.flights, other.flights)

    def dict(self) -> dict[str, Any]:
        return {"name": self.name, "flights": [o.dict() for o in self.flights]}
