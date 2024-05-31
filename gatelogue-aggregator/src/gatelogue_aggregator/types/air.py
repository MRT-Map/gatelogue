from __future__ import annotations

import copy
from typing import Literal, Self, override

import msgspec
import rich

from gatelogue_aggregator.types.base import IdObject, MergeableObject, Sourced, ToSerializable


class Flight(IdObject, ToSerializable, kw_only=True):
    codes: set[str]
    gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)
    airline: Sourced[Airline]

    @override
    class SerializableClass(msgspec.Struct):
        codes: set[str]
        gates: list[Sourced.SerializableClass[str]]
        airline: Sourced.SerializableClass[str]

    @override
    def ser(self) -> SerializableClass:
        return self.SerializableClass(codes=self.codes, gates=[o.ser() for o in self.gates], airline=self.airline.ser())

    @override
    def ctx(self, ctx: AirContext):
        ctx.flight.append(self)

    @override
    def update(self):
        new_gates = []
        for gate in self.gates:
            try:
                existing_gate = next(a for a in new_gates if gate.v.airport.equivalent(gate.v.airport))
            except StopIteration:
                new_gates.append(gate)
                continue
            if existing_gate.v.code is None and gate.v.code is not None:
                new_gates.remove(existing_gate)
                existing_gate.v.flights = [a for a in existing_gate.v.flights if a.v != self]
                new_gates.append(gate)
            elif existing_gate.v.code is not None and gate.v.code is None:
                gate.v.flights = [a for a in gate.v.flights if a.v != self]
        self.gates = [v for _, v in {str(a.v.id): a for a in new_gates}.items()]
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


class Airport(IdObject, ToSerializable, kw_only=True):
    code: str
    name: Sourced[str] | None = None
    world: Sourced[Literal["Old", "New"]] | None = None
    coordinates: Sourced[tuple[int, int]] | None = None
    link: Sourced[str] | None = None
    gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)

    @override
    class SerializableClass(msgspec.Struct):
        code: str
        name: Sourced.SerializableClass[str] | None
        world: Sourced.SerializableClass[str] | None
        coordinates: Sourced.SerializableClass[tuple[int, int]] | None
        link: Sourced.SerializableClass[str] | None
        gates: list[Sourced.SerializableClass[str]]

    @override
    def ser(self) -> SerializableClass:
        return self.SerializableClass(
            code=self.code,
            name=self.name.ser() if self.name is not None else None,
            world=self.world.ser() if self.world is not None else None,
            coordinates=self.coordinates.ser() if self.coordinates is not None else None,
            link=self.link.ser() if self.link is not None else None,
            gates=[o.ser() for o in self.gates],
        )

    @override
    def ctx(self, ctx: AirContext):
        ctx.airport.append(self)

    @override
    def update(self):
        for gate in self.gates:
            gate.v.airport = self.source(gate)
        self.gates = [v for _, v in {str(a.v.id): a for a in self.gates}.items()]

    def equivalent(self, other: Self) -> bool:
        return self.code == other.code

    def merge(self, other: Self):
        if other.id != self.id:
            other.id.id = self.id
        else:
            return
        self.name = self.name or other.name
        self.world = self.world or other.world
        self.coordinates = self.coordinates or other.coordinates
        self.link = self.link or other.link
        MergeableObject.merge_lists(self.gates, other.gates)


class Gate(IdObject, ToSerializable, kw_only=True):
    code: str | None
    flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)
    airport: Sourced[Airport]
    size: Sourced[str] | None = None

    @override
    class SerializableClass(msgspec.Struct):
        code: str | None
        flights: list[Sourced.SerializableClass[str]]
        airport: Sourced.SerializableClass[str]
        size: Sourced.SerializableClass[str] | None

    @override
    def ser(self) -> SerializableClass:
        return self.SerializableClass(
            code=self.code,
            flights=[o.ser() for o in self.flights],
            airport=self.airport.ser(),
            size=self.size.ser() if self.size is not None else None,
        )

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
        self.flights = [v for _, v in {str(a.v.id): a for a in self.flights}.items()]

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


class Airline(IdObject, ToSerializable, kw_only=True):
    name: str
    flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)
    link: Sourced[str] | None = None

    @override
    class SerializableClass(msgspec.Struct):
        name: str
        flights: list[Sourced.SerializableClass[str]]
        link: Sourced.SerializableClass[str] | None

    @override
    def ser(self) -> SerializableClass:
        return self.SerializableClass(
            name=self.name,
            flights=[o.ser() for o in self.flights],
            link=self.link.ser() if self.link is not None else None,
        )

    @override
    def ctx(self, ctx: AirContext):
        ctx.airline.append(self)

    @override
    def update(self):
        for flight in self.flights:
            flight.v.airline = self.source(flight)
        self.flights = [v for _, v in {str(a.v.id): a for a in self.flights}.items()]

    def equivalent(self, other: Self) -> bool:
        return self.name == other.name

    def merge(self, other: Self):
        if other.id != self.id:
            other.id.id = self.id
        else:
            return
        MergeableObject.merge_lists(self.flights, other.flights)
        self.link = self.link or other.link


class AirContext(ToSerializable):
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

    @override
    class SerializableClass(msgspec.Struct):
        flight: dict[str, Flight.SerializableClass]
        airport: dict[str, Airport.SerializableClass]
        gate: dict[str, Gate.SerializableClass]
        airline: dict[str, Airline.SerializableClass]

    @override
    def ser(self) -> SerializableClass:
        return self.SerializableClass(
            flight={str(o.id): o.ser() for o in self.flight},
            airport={str(o.id): o.ser() for o in self.airport},
            gate={str(o.id): o.ser() for o in self.gate},
            airline={str(o.id): o.ser() for o in self.airline},
        )
