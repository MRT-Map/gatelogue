from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from gatelogue_aggregator.types.base import BaseObject, Sourced

if TYPE_CHECKING:
    from gatelogue_aggregator.types.context import AirContext


class Flight(BaseObject, kw_only=True):
    codes: list[str]
    gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)
    airline: Sourced[Airline]

    def ctx(self, ctx: AirContext):
        ctx.flight.append(self)

    def update(self):
        for gate in self.gates:
            if self not in (o.v for o in gate.v.flights):
                gate.v.flights.append(Sourced(self))
        if self not in (o.v for o in self.airline.v.flights):
            self.airline.v.flights.append(Sourced(self))


class Airport(BaseObject, kw_only=True):
    code: str
    coordinates: Sourced[tuple[int, int]] | None = None
    gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)

    def ctx(self, ctx: AirContext):
        ctx.airport.append(self)

    def update(self):
        for gate in self.gates:
            gate.v.airport = Sourced(self)


class Gate(BaseObject, kw_only=True):
    code: str | None
    flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)
    airport: Sourced[Airport]
    size: Sourced[str] | None = None

    def ctx(self, ctx: AirContext):
        ctx.gate.append(self)

    def update(self):
        for flight in self.flights:
            if self not in (o.v for o in flight.v.gates):
                flight.v.gates.append(Sourced(self))
        if self not in (o.v for o in self.airport.v.gates):
            self.airport.v.gates.append(Sourced(self))


class Airline(BaseObject, kw_only=True):
    name: str
    flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)

    def ctx(self, ctx: AirContext):
        ctx.airline.append(self)

    def update(self):
        for flight in self.flights:
            flight.v.airline = Sourced(self)
