from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Literal, Self, override

import msgspec
import rich.progress

from gatelogue_aggregator.sources.air.hardcode import DIRECTIONAL_FLIGHT_AIRLINES, AIRLINE_ALIASES, AIRPORT_ALIASES
from gatelogue_aggregator.types.base import BaseContext, Node, Source, Sourced

if TYPE_CHECKING:
    from collections.abc import Container


class _AirContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Flight(Node[_AirContext]):
    acceptable_list_node_types = lambda: (Gate,)  # noqa: E731
    acceptable_single_node_types = lambda: (Airline,)  # noqa: E731

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

        @staticmethod
        @override
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
        gates: list[Sourced.Ser[str]]
        airline: Sourced.Ser[str]

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

    def update(self, ctx: AirContext):
        processed_gates: list[Gate] = []
        gates = list(self.get_all(ctx, Gate))
        for gate in gates:
            if (
                existing := next(
                    (a for a in processed_gates if a.get_one(ctx, Airport).equivalent(ctx, gate.get_one(ctx, Airport))),
                    None,
                )
            ) is None:
                processed_gates.append(gate)
            elif existing.merged_attr(ctx, "code") is None and gate.merged_attr(ctx, "code") is not None:
                processed_gates.remove(existing)
                self.disconnect_all(ctx, existing)
                processed_gates.append(gate)
            elif existing.merged_attr(ctx, "code") is not None and gate.merged_attr(ctx, "code") is None:
                self.disconnect_all(ctx, gate)
            elif existing.merged_attr(ctx, "code") == gate.merged_attr(ctx, "code"):
                existing.merge(ctx, gate)

    @staticmethod
    def process_code[T: (str, None)](s: T, airline_name: str | None = None) -> set[T]:
        s = Node.process_code(s)
        direction = DIRECTIONAL_FLIGHT_AIRLINES.get(airline_name)
        if not s.isdigit() or direction is None:
            return {s}
        if direction == "odd-even":
            if int(s) % 2 == 1:
                return {s, str(int(s) + 1)}
            return {s, str(int(s) - 1)}
        if int(s) % 2 == 1:
            return {s, str(int(s) - 1)}
        return {s, str(int(s) + 1)}


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Airport(Node[_AirContext]):
    acceptable_list_node_types = lambda: (Gate,)  # noqa: E731

    @override
    def __init__(self, ctx: AirContext, source: type[AirContext] | None = None, *, code: str, **attrs):
        super().__init__(ctx, source, code=code, **attrs)

    @override
    def str_ctx(self, ctx: AirContext, filter_: Container[str] | None = None) -> str:
        return super().str_ctx(ctx, filter_ or {"code"})

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str
        name: str | None = None
        world: Literal["Old", "New"] | None = None
        coordinates: tuple[int, int] | None = None
        link: str | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            if k in ("name", "world", "coordinates", "link"):
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "name")
            self.sourced_merge(source, existing, "world")
            self.sourced_merge(source, existing, "coordinates")
            self.sourced_merge(source, existing, "link")

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
        gates: list[Sourced.Ser[str]]

    def ser(self, ctx: AirContext) -> Flight.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            gates=self.get_all_ser(ctx, Gate),
        )

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        return self.merged_attr(ctx, "code") == other.merged_attr(ctx, "code")

    @override
    def key(self, ctx: AirContext) -> str:
        return self.merged_attr(ctx, "code")

    def update(self, ctx: AirContext):
        if (
            none_gate := next((a for a in self.get_all(ctx, Gate) if a.merged_attr(ctx, "code") is None), None)
        ) is None:
            return
        for flight in list(none_gate.get_all(ctx, Flight)):
            possible_gates = []
            for possible_gate in self.get_all(ctx, Gate):
                if possible_gate.merged_attr(ctx, "code") is None:
                    continue
                if (airline := possible_gate.get_one(ctx, Airline)) is None:
                    continue
                if airline.equivalent(ctx, flight.get_one(ctx, Airline)):
                    possible_gates.append(possible_gate)
            if len(possible_gates) == 1:
                new_gate = possible_gates[0]
                sources = {a["s"] for a in ctx.g[none_gate][flight].values()} | {
                    a["s"] for a in ctx.g[self][new_gate].values()
                }
                flight.disconnect_all(ctx, none_gate)
                for source in sources:
                    flight.connect(ctx, new_gate, source)

    @staticmethod
    @override
    def process_code[T: (str, None)](s: T) -> T:
        s = AIRPORT_ALIASES.get(s, s)
        if s is None:
            return None
        s = str(s).upper()
        if len(s) == 4 and s[3] == "T":  # noqa: PLR2004
            return s[:3]
        return s


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Gate(Node[_AirContext]):
    acceptable_list_node_types = lambda: (Flight,)  # noqa: E731
    acceptable_single_node_types = lambda: (Airport, Airline)  # noqa: E731

    @override
    def __init__(
        self, ctx: AirContext, source: type[AirContext] | None = None, *, code: str | None, airport: Airport, **attrs
    ):
        super().__init__(ctx, source, code=code, **attrs)
        self.connect_one(ctx, airport, source)

    @override
    def str_ctx(self, ctx: AirContext, filter_: Container[str] | None = None) -> str:
        code = self.merged_attr(ctx, "code")
        airport = self.get_one(ctx, Airport).merged_attr(ctx, "code")
        return type(self).__name__ + f"(code={code},airport={airport})"

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str | None
        size: str | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            if k == "size":
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "size")

    @override
    def attrs(self, ctx: AirContext, source: type[AirContext] | None = None) -> Gate.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: AirContext) -> dict[Source, Gate.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        code: str | None
        flights: list[Sourced.Ser[str]]
        airport: Sourced.Ser[str]
        airline: Sourced.Ser[str] | None
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
        return self.merged_attr(ctx, "code") == other.merged_attr(ctx, "code") and self.get_one(
            ctx, Airport
        ).equivalent(ctx, other.get_one(ctx, Airport))

    @override
    def key(self, ctx: AirContext) -> str:
        return self.merged_attr(ctx, "code")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Airline(Node[_AirContext]):
    acceptable_list_node_types = lambda: (Flight,)  # noqa: E731

    @override
    def __init__(self, ctx: AirContext, source: type[AirContext] | None = None, *, name: str, **attrs):
        super().__init__(ctx, source, name=name, **attrs)

    @override
    def str_ctx(self, ctx: AirContext, filter_: Container[str] | None = None) -> str:
        return super().str_ctx(ctx, filter_ or {"name"})

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        name: str
        link: str | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "name":
                return v
            if k == "link":
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "link")

    @override
    def attrs(self, ctx: AirContext, source: type[AirContext] | None = None) -> Airline.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: AirContext) -> dict[Source, Airline.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        name: str
        flights: list[Sourced.Ser[str]]
        link: Sourced.Ser[str] | None

    def ser(self, ctx: AirContext) -> Flight.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            flights=self.get_all_ser(ctx, Flight),
        )

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        return self.merged_attr(ctx, "name") == other.merged_attr(ctx, "name")

    @override
    def key(self, ctx: AirContext) -> str:
        return self.merged_attr(ctx, "name")

    @staticmethod
    def process_airline_name[T: (str, None)](s: T) -> T:
        return AIRLINE_ALIASES.get(s, s)


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
            if n.merged_attr(self, "code") == code:
                return n
        return Airport(self, source, code=code, **attrs)

    def gate(self, source: type[AirContext] | None = None, *, code: str | None, airport: Airport, **attrs) -> Gate:
        for n in self.g.nodes:
            if not isinstance(n, Gate):
                continue
            if n.merged_attr(self, "code") == code and n.get_one(self, Airport).equivalent(self, airport):
                return n
        return Gate(self, source, code=code, airport=airport, **attrs)

    def airline(self, source: type[AirContext] | None = None, *, name: str, **attrs) -> Airline:
        for n in self.g.nodes:
            if not isinstance(n, Airline):
                continue
            if n.merged_attr(self, "name") == name:
                return n
        return Airline(self, source, name=name, **attrs)

    def update(self):
        for node in rich.progress.track(self.g.nodes, "[yellow]Updating air nodes"):
            if isinstance(node, Flight | Airport):
                node.update(self)


class AirSource(AirContext, Source):
    pass
