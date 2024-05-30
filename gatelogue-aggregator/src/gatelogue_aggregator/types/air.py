from __future__ import annotations

from typing import Any, Self, override

import msgspec

from gatelogue_aggregator.types.base import IdObject, MergeableObject, Sourced


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
        self.airline.merge(other.airline)

        MergeableObject.merge_lists(self.gates, other.gates)
        new_gates = []
        for g in self.gates:
            code_filled = [a for a in other.gates if a.v.code is not None and a.v.airport.equivalent(g.v.airport)]
            if g.v.code is None and len(code_filled) != 0:
                new_gates.append(code_filled[0])
                g.v.flights = [a for a in g.v.flights if a.v != self]
            else:
                new_gates.append(g)
        self.gates = new_gates

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
