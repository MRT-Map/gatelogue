from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal, Self, override, Any

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Node, Source, Sourced

if TYPE_CHECKING:
    import uuid


class _AirContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Flight(Node[_AirContext]):
    acceptable_list_node_types = lambda: (Gate,)
    acceptable_single_node_types = lambda: (Airline,)

    @override
    def __init__(
        self, ctx: AirContext, source: type[AirContext] | None = None, *, codes: set[str], airline: Airline, **attrs
    ):
        super().__init__(ctx, source, codes=codes, **attrs)
        self.connect_one(ctx, airline, source)

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        codes: set[str]

        @override
        @staticmethod
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "codes":
                return v
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            existing["codes"].update(self.codes)

    @override
    def attrs(self, ctx: AirContext, source: type[AirContext] | None = None) -> Flight.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: AirContext) -> dict[Source, Flight.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        codes: set[str]
        gates: list[Sourced.Ser[uuid.UUID]]
        airline: Sourced.Ser[uuid.UUID]

    def ser(self, ctx: AirContext) -> Flight.Ser:
        return self.Ser(
            **self.merged_attrs(ctx), gates=self.get_all_ser(ctx, Gate), airline=self.get_one_ser(ctx, Airline)
        )

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        return len(
            {a for _, c in self.all_attrs(ctx).items() for a in c.codes}.intersection(
                {a for _, c in other.all_attrs(ctx).items() for a in c.codes}
            )
        ) != 0 and self.get_one(ctx, Airline).equivalent(ctx, other.get_one(ctx, Airline))

    @override
    def key(self, ctx: AirContext) -> str:
        return self.get_one(ctx, Airline).key(ctx)


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Airport(Node[_AirContext]):
    acceptable_list_node_types = lambda: (Gate,)

    @override
    def __init__(self, ctx: AirContext, source: type[AirContext] | None = None, *, code: str, **attrs):
        super().__init__(ctx, source, code=code, **attrs)

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str
        name: str | None = None
        world: Literal["Old", "New"] | None = None
        coordinates: tuple[int, int] | None = None
        link: str | None = None

        @override
        @staticmethod
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            elif k in ("name", "world", "coordinates", "link"):
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            if existing["name"] is not None and self.name == existing["name"].v:
                existing["name"].s.add(source.name)
            if self.name is not None:
                existing["name"] = existing["name"] or Sourced(self.name).source(source)

            if existing["world"] is not None and self.world == existing["world"].v:
                existing["world"].s.add(source.name)
            if self.world is not None:
                existing["world"] = existing["world"] or Sourced(self.world).source(source)

            if existing["coordinates"] is not None and self.coordinates == existing["coordinates"].v:
                existing["coordinates"].s.add(source.name)
            if self.coordinates is not None:
                existing["coordinates"] = existing["coordinates"] or Sourced(self.coordinates).source(source)

            if existing["link"] is not None and self.link == existing["link"].v:
                existing["link"].s.add(source.name)
            if self.link is not None:
                existing["link"] = existing["link"] or Sourced(self.link).source(source)

    @override
    def attrs(self, ctx: AirContext, source: type[AirContext] | None = None) -> Airport.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: AirContext) -> dict[Source, Airport.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        code: str
        name: Sourced.Ser[str] | None
        world: Sourced.Ser[str] | None
        coordinates: Sourced.Ser[tuple[int, int]] | None
        link: Sourced.Ser[str] | None
        gates: list[Sourced.Ser[uuid.UUID]]

    def ser(self, ctx: AirContext) -> Flight.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            gates=self.get_all_ser(ctx, Gate),
        )

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        self_attrs = sorted(self.all_attrs(ctx).items())[0][1]
        other_attrs = sorted(other.all_attrs(ctx).items())[0][1]
        return self_attrs.code == other_attrs.code

    @override
    def key(self, ctx: AirContext) -> str:
        return sorted(self.all_attrs(ctx).items())[0][1].code


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Gate(Node[_AirContext]):
    acceptable_list_node_types = lambda: (Flight,)
    acceptable_single_node_types = lambda: (Airport, Airline)

    @override
    def __init__(
        self, ctx: AirContext, source: type[AirContext] | None = None, *, code: str | None, airport: Airport, **attrs
    ):
        super().__init__(ctx, source, code=code, **attrs)
        self.connect_one(ctx, airport, source)

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str | None
        size: str | None = None

        @override
        @staticmethod
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            elif k == "size":
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            if existing["size"] is not None and self.size == existing["size"].v:
                existing["size"].s.add(source.name)
            if self.size is not None:
                existing["size"] = existing["size"] or Sourced(self.size).source(source)

    @override
    def attrs(self, ctx: AirContext, source: type[AirContext] | None = None) -> Gate.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: AirContext) -> dict[Source, Gate.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        code: str | None
        flights: list[Sourced.Ser[uuid.UUID]]
        airport: Sourced.Ser[uuid.UUID]
        airline: Sourced.Ser[uuid.UUID] | None
        size: Sourced.Ser[str] | None

    def ser(self, ctx: AirContext) -> Flight.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            flights=self.get_all_ser(ctx, Flight),
            airport=self.get_one_ser(ctx, Airport),
            airline=self.get_one_ser(ctx, Airline),
        )

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        self_attrs = sorted(self.all_attrs(ctx).items())[0][1]
        other_attrs = sorted(other.all_attrs(ctx).items())[0][1]
        return self_attrs.code == other_attrs.code and self.get_one(ctx, Airport).equivalent(
            ctx, other.get_one(ctx, Airport)
        )

    @override
    def key(self, ctx: AirContext) -> str:
        return sorted(self.all_attrs(ctx).items())[0][1].code


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Airline(Node[_AirContext]):
    acceptable_list_node_types = lambda: (Flight,)

    @override
    def __init__(self, ctx: AirContext, source: type[AirContext] | None = None, *, name: str, **attrs):
        super().__init__(ctx, source, name=name, **attrs)

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        name: str
        link: str | None = None

        @override
        @staticmethod
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "name":
                return v
            elif k == "link":
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            if existing["link"] is not None and self.link == existing["link"].v:
                existing["link"].s.add(source.name)
            if self.link is not None:
                existing["link"] = existing["link"] or Sourced(self.link).source(source)

    @override
    def attrs(self, ctx: AirContext, source: type[AirContext] | None = None) -> Airline.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: AirContext) -> dict[Source, Airline.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        name: str
        flights: list[Sourced.Ser[uuid.UUID]]
        link: Sourced.Ser[str] | None

    def ser(self, ctx: AirContext) -> Flight.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            flights=self.get_all_ser(ctx, Flight),
        )

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        self_attrs = sorted(self.all_attrs(ctx).items())[0][1]
        other_attrs = sorted(other.all_attrs(ctx).items())[0][1]
        return self_attrs.name == other_attrs.name

    @override
    def key(self, ctx: AirContext) -> str:
        return sorted(self.all_attrs(ctx).items())[0][1].name


class AirContext(_AirContext):
    @override
    class Ser(msgspec.Struct):
        flight: dict[str, Flight.Ser]
        airport: dict[str, Airport.Ser]
        gate: dict[str, Gate.Ser]
        airline: dict[str, Airline.Ser]

    def ser(self) -> AirContext.Ser:
        return self.Ser(
            flight={str(a.id): a.ser(self) for a in self.g.nodes if isinstance(a, Flight)},
            airport={str(a.id): a.ser(self) for a in self.g.nodes if isinstance(a, Airport)},
            gate={str(a.id): a.ser(self) for a in self.g.nodes if isinstance(a, Gate)},
            airline={str(a.id): a.ser(self) for a in self.g.nodes if isinstance(a, Airline)},
        )

    def flight(self, source: type[AirContext] | None = None, *, codes: set[str], airline: Airline, **attrs) -> Flight:
        for n in self.g.nodes:
            if not isinstance(n, Flight):
                continue
            if len({a for _, c in n.all_attrs(self).items() for a in c.codes}.intersection(codes)) != 0 and n.get_one(
                self, Airline
            ).equivalent(self, airline):
                return n
        return Flight(self, source, codes=codes, airline=airline, **attrs)

    def airport(self, source: type[AirContext] | None = None, *, code: str, **attrs) -> Airport:
        for n in self.g.nodes:
            if not isinstance(n, Airport):
                continue
            self_attrs = sorted(n.all_attrs(self).items())[0][1]
            if self_attrs.code == code:
                return n
        return Airport(self, source, code=code, **attrs)

    def gate(self, source: type[AirContext] | None = None, *, code: str | None, airport: Airport, **attrs) -> Gate:
        for n in self.g.nodes:
            if not isinstance(n, Gate):
                continue
            self_attrs = sorted(n.all_attrs(self).items())[0][1]
            if self_attrs.code == code and n.get_one(self, Airport).equivalent(self, airport):
                return n
        return Gate(self, source, code=code, airport=airport, **attrs)

    def airline(self, source: type[AirContext] | None = None, *, name: str, **attrs) -> Airline:
        for n in self.g.nodes:
            if not isinstance(n, Airline):
                continue
            self_attrs = sorted(n.all_attrs(self).items())[0][1]
            if self_attrs.name == name:
                return n
        return Airline(self, source, name=name, **attrs)

    def update(self):
        # TODO: resolve flights with unknown gates (None+other flight known, None+airport known)
        pass


class AirSource(AirContext, Source):
    pass


#
# from __future__ import annotations
#
# import contextlib
# from typing import Literal, Self, override
#
# import msgspec
#
# from gatelogue_aggregator.types.base import BaseContext, IdObject, MergeableObject, Sourced, ToSerializable
#
#
# class Flight(IdObject, ToSerializable, kw_only=True):
#     codes: set[str]
#     gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)
#     airline: Sourced[Airline]
#
#     @override
#     class SerializableClass(msgspec.Struct):
#         codes: set[str]
#         gates: list[Sourced.SerializableClass[str]]
#         airline: Sourced.SerializableClass[str]
#
#     @override
#     def ser(self) -> SerializableClass:
#         return self.SerializableClass(codes=self.codes, gates=[o.ser() for o in self.gates], airline=self.airline.ser())
#
#     @override
#     def ctx(self, ctx: AirContext):
#         ctx.flight.append(self)
#
#     @override
#     def de_ctx(self, ctx: AirContext):
#         with contextlib.suppress(ValueError):
#             ctx.flight.remove(self)
#
#     @override
#     def update(self, ctx: AirContext):
#         new_gates = []
#         for gate in self.gates:
#             try:
#                 existing_gate = next(a for a in new_gates if gate.v.airport.equivalent(a.v.airport))
#             except StopIteration:
#                 new_gates.append(gate)
#                 continue
#             if existing_gate.v.code is None and gate.v.code is not None:
#                 new_gates.remove(existing_gate)
#                 existing_gate.v.flights = [a for a in existing_gate.v.flights if a.v != self]
#                 new_gates.append(gate)
#             elif existing_gate.v.code is not None and gate.v.code is None:
#                 gate.v.flights = [a for a in gate.v.flights if a.v != self]
#             elif existing_gate.v.code == gate.v.code:
#                 existing_gate.merge(ctx, gate)
#         self.gates = [v for _, v in {str(a.v.id): a for a in new_gates}.items()]
#
#         for gate in self.gates:
#             if len([o for o in gate.v.flights if o.v is self]) == 0:
#                 gate.v.flights.append(self.source(gate))
#         if self not in (o.v for o in self.airline.v.flights):
#             self.airline.v.flights.append(self.source(self.airline))
#
#     def equivalent(self, other: Self) -> bool:
#         return len(self.codes.intersection(other.codes)) != 0 and self.airline.equivalent(other.airline)
#
#     def merge(self, ctx: AirContext, other: Self):
#         if other.id != self.id:
#             other.id.id = self.id
#             other.de_ctx(ctx)
#         else:
#             return
#         self.codes.update(other.codes)
#         self.airline.merge(ctx, other.airline)
#         MergeableObject.merge_lists(ctx, self.gates, other.gates)
#
#
# class Airport(IdObject, ToSerializable, kw_only=True):
#     code: str
#     name: Sourced[str] | None = None
#     world: Sourced[Literal["Old", "New"]] | None = None
#     coordinates: Sourced[tuple[int, int]] | None = None
#     link: Sourced[str] | None = None
#     gates: list[Sourced[Gate]] = msgspec.field(default_factory=list)
#
#     @override
#     class SerializableClass(msgspec.Struct):
#         code: str
#         name: Sourced.SerializableClass[str] | None
#         world: Sourced.SerializableClass[str] | None
#         coordinates: Sourced.SerializableClass[tuple[int, int]] | None
#         link: Sourced.SerializableClass[str] | None
#         gates: list[Sourced.SerializableClass[str]]
#
#     @override
#     def ser(self) -> SerializableClass:
#         return self.SerializableClass(
#             code=self.code,
#             name=self.name.ser() if self.name is not None else None,
#             world=self.world.ser() if self.world is not None else None,
#             coordinates=self.coordinates.ser() if self.coordinates is not None else None,
#             link=self.link.ser() if self.link is not None else None,
#             gates=[o.ser() for o in self.gates],
#         )
#
#     @override
#     def ctx(self, ctx: AirContext):
#         ctx.airport.append(self)
#
#     @override
#     def de_ctx(self, ctx: AirContext):
#         with contextlib.suppress(ValueError):
#             ctx.airport.remove(self)
#
#     @override
#     def update(self, ctx: AirContext):
#         for gate in self.gates:
#             gate.v.airport = self.source(gate)
#         self.gates = [v for _, v in {str(a.v.id): a for a in self.gates}.items()]
#
#     def final_update(self):
#         try:
#             none_gate = next(a.v for a in self.gates if a.v.code is None)
#         except StopIteration:
#             return
#         new_flights = []
#         for flight in none_gate.flights:
#             possible_gates = [
#                 a
#                 for a in self.gates
#                 if a.v.code is not None and a.v.airline is not None and a.v.airline.v.equivalent(flight.v.airline.v)
#             ]
#             if len(possible_gates) == 1:
#                 flight.s.update(possible_gates[0].s)
#                 flight.v.gates = [a for a in flight.v.gates if a.v != none_gate]
#                 flight.v.gates.append(possible_gates[0])
#                 possible_gates[0].v.flights.append(flight)
#             else:
#                 new_flights.append(flight)
#         none_gate.flights = new_flights
#
#     def equivalent(self, other: Self) -> bool:
#         return self.code == other.code
#
#     def merge(self, ctx: AirContext, other: Self):
#         if other.id != self.id:
#             other.id.id = self.id
#             other.de_ctx(ctx)
#         else:
#             return
#         self.name = self.name or other.name
#         self.world = self.world or other.world
#         self.coordinates = self.coordinates or other.coordinates
#         self.link = self.link or other.link
#         MergeableObject.merge_lists(ctx, self.gates, other.gates)
#
#
# class Gate(IdObject, ToSerializable, kw_only=True):
#     code: str | None
#     flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)
#     airport: Sourced[Airport]
#     airline: Sourced[Airline] | None = None
#     size: Sourced[str] | None = None
#
#     @override
#     class SerializableClass(msgspec.Struct):
#         code: str | None
#         flights: list[Sourced.SerializableClass[str]]
#         airport: Sourced.SerializableClass[str]
#         airline: Sourced.SerializableClass[str] | None
#         size: Sourced.SerializableClass[str] | None
#
#     @override
#     def ser(self) -> SerializableClass:
#         return self.SerializableClass(
#             code=self.code,
#             flights=[o.ser() for o in self.flights],
#             airport=self.airport.ser(),
#             airline=self.airline.ser() if self.airline is not None else None,
#             size=self.size.ser() if self.size is not None else None,
#         )
#
#     @override
#     def ctx(self, ctx: AirContext):
#         ctx.gate.append(self)
#
#     @override
#     def de_ctx(self, ctx: AirContext):
#         with contextlib.suppress(ValueError):
#             ctx.gate.remove(self)
#
#     @override
#     def update(self, ctx: AirContext):
#         for flight in self.flights:
#             if self not in (o.v for o in flight.v.gates):
#                 flight.v.gates.append(self.source(flight))
#         if self not in (o.v for o in self.airport.v.gates):
#             self.airport.v.gates.append(self.source(self.airport))
#         self.flights = [v for _, v in {str(a.v.id): a for a in self.flights}.items()]
#
#     def equivalent(self, other: Self) -> bool:
#         return self.code == other.code and self.airport.equivalent(other.airport)
#
#     def merge(self, ctx: AirContext, other: Self):
#         if other.id != self.id:
#             other.id.id = self.id
#             other.de_ctx(ctx)
#         else:
#             return
#         self.size = self.size or other.size
#         self.airline = self.airline or other.airline
#         MergeableObject.merge_lists(ctx, self.flights, other.flights)
#         self.airport.merge(ctx, other.airport)
#
#
# class Airline(IdObject, ToSerializable, kw_only=True):
#     name: str
#     flights: list[Sourced[Flight]] = msgspec.field(default_factory=list)
#     link: Sourced[str] | None = None
#
#     @override
#     class SerializableClass(msgspec.Struct):
#         name: str
#         flights: list[Sourced.SerializableClass[str]]
#         link: Sourced.SerializableClass[str] | None
#
#     @override
#     def ser(self) -> SerializableClass:
#         return self.SerializableClass(
#             name=self.name,
#             flights=[o.ser() for o in self.flights],
#             link=self.link.ser() if self.link is not None else None,
#         )
#
#     @override
#     def ctx(self, ctx: AirContext):
#         ctx.airline.append(self)
#
#     @override
#     def de_ctx(self, ctx: AirContext):
#         with contextlib.suppress(ValueError):
#             ctx.airline.remove(self)
#
#     @override
#     def update(self, ctx: AirContext):
#         for flight in self.flights:
#             flight.v.airline = self.source(flight)
#         self.flights = [v for _, v in {str(a.v.id): a for a in self.flights}.items()]
#
#     def equivalent(self, other: Self) -> bool:
#         return self.name == other.name
#
#     def merge(self, ctx: AirContext, other: Self):
#         if other.id != self.id:
#             other.id.id = self.id
#             other.de_ctx(ctx)
#         else:
#             return
#         MergeableObject.merge_lists(ctx, self.flights, other.flights)
#         self.link = self.link or other.link
#
#
# class AirContext(BaseContext):
#     __slots__ = ("flight", "airport", "gate", "airline")
#     flight: list[Flight]
#     airport: list[Airport]
#     gate: list[Gate]
#     airline: list[Airline]
#
#     def __init__(self):
#         self.flight = []
#         self.airport = []
#         self.gate = []
#         self.airline = []
#
#     def get_flight(self, **query) -> Flight:
#         for o in self.flight:
#             if all(v == getattr(o, k) for k, v in query.items()):
#                 return o
#         o = Flight(**query)
#         o.ctx(self)
#         return o
#
#     def get_airport(self, **query) -> Airport:
#         for o in self.airport:
#             if all(v == getattr(o, k) for k, v in query.items()):
#                 return o
#         o = Airport(**query)
#         o.ctx(self)
#         return o
#
#     def get_gate(self, **query) -> Gate:
#         for o in self.gate:
#             if all(v == getattr(o, k) for k, v in query.items()):
#                 return o
#         o = Gate(**query)
#         o.ctx(self)
#         return o
#
#     def get_airline(self, **query) -> Airline:
#         for o in self.airline:
#             if all(v == getattr(o, k) for k, v in query.items()):
#                 return o
#         o = Airline(**query)
#         o.ctx(self)
#         return o
#
#     def update(self):
#         for o in self.flight:
#             o.update(self)
#         for o in self.airport:
#             o.update(self)
#         for o in self.gate:
#             o.update(self)
#         for o in self.airline:
#             o.update(self)
#
#     def final_update(self):
#         for airport in self.airport:
#             airport.final_update()
#
#     @override
#     class SerializableClass(msgspec.Struct):
#         flight: dict[str, Flight.SerializableClass]
#         airport: dict[str, Airport.SerializableClass]
#         gate: dict[str, Gate.SerializableClass]
#         airline: dict[str, Airline.SerializableClass]
#
#     @override
#     def ser(self) -> SerializableClass:
#         return self.SerializableClass(
#             flight={str(o.id): o.ser() for o in self.flight},
#             airport={str(o.id): o.ser() for o in self.airport},
#             gate={str(o.id): o.ser() for o in self.gate},
#             airline={str(o.id): o.ser() for o in self.airline},
#         )
