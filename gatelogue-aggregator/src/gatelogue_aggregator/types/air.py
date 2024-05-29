from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

import msgspec

from gatelogue_aggregator.types.base import BaseObject, Sourced

if TYPE_CHECKING:
    from gatelogue_aggregator.types.context import AirContext


class Flight(BaseObject, kw_only=True):
    codes: list[str]
    gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)
    airline: Sourced[Airline]

    @override
    def ctx(self, ctx: AirContext):
        ctx.flight.append(self)

    @override
    def update(self):
        for gate in self.gates:
            if self not in (o.v for o in gate.v.flights):
                gate.v.flights.append(Sourced(self).source(gate))
        if self not in (o.v for o in self.airline.v.flights):
            self.airline.v.flights.append(Sourced(self).source(self.airline))

    def dict(self) -> dict[str, Any]:
        return {"codes": self.codes, "gates": [o.dict() for o in self.gates], "airline": self.airline.dict()}


class Airport(BaseObject, kw_only=True):
    code: str
    coordinates: Sourced[tuple[int, int]] | None = None
    gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)

    @override
    def ctx(self, ctx: AirContext):
        ctx.airport.append(self)

    @override
    def update(self):
        for gate in self.gates:
            gate.v.airport = Sourced(self).source(gate)

    def dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "coordinates": self.coordinates.dict() if self.coordinates is not None else None,
            "gates": [o.dict() for o in self.gates],
        }


class Gate(BaseObject, kw_only=True):
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
                flight.v.gates.append(Sourced(self).source(flight))
        if self not in (o.v for o in self.airport.v.gates):
            self.airport.v.gates.append(Sourced(self).source(self.airport))

    def dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "flights": [o.dict() for o in self.flights],
            "airport": self.airport.dict(),
            "size": self.size.dict() if self.size is not None else None,
        }


class Airline(BaseObject, kw_only=True):
    name: str
    flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)

    @override
    def ctx(self, ctx: AirContext):
        ctx.airline.append(self)

    @override
    def update(self):
        for flight in self.flights:
            flight.v.airline = Sourced(self).source(flight)

    def dict(self) -> dict[str, Any]:
        return {"name": self.name, "flights": [o.dict() for o in self.flights]}
