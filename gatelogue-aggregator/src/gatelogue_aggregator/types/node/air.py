from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, ClassVar, Literal, Self, override

from gatelogue_aggregator.logging import INFO1, track
from gatelogue_aggregator.sources.air.hardcode import AIRLINE_ALIASES, AIRPORT_ALIASES, DIRECTIONAL_FLIGHT_AIRLINES
from gatelogue_aggregator.types.base import BaseContext, Source, Sourced
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef

if TYPE_CHECKING:
    from collections.abc import Iterable


class _AirContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class AirFlight(Node[_AirContext]):
    acceptable_list_node_types: ClassVar = lambda: (AirGate,)
    acceptable_single_node_types: ClassVar = lambda: (AirAirline,)

    codes: set[str]
    """Unique flight code(s). **2-letter airline prefix not included**"""

    # noinspection PyDataclass
    gates: list[Sourced[int]] = None
    """List of IDs of :py:class:`AirGate` s that the flight goes to. Should be of length 2 in most cases"""
    airline: Sourced[int] = None
    """ID of the :py:class:`AirAirline` the flight is operated by"""

    def __init__(
        self,
        ctx: AirContext,
        *,
        codes: set[str],
        airline: AirAirline,
    ):
        super().__init__(ctx)
        self.codes = codes
        self.connect_one(ctx, airline, ctx.source(None))

    @override
    def str_ctx(self, ctx: AirContext) -> str:
        airline_name = self.get_one(ctx, AirAirline).name
        code = "/".join(self.codes)
        return f"{airline_name} {code}"

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, AirAirline).equivalent(
            ctx, other.get_one(ctx, AirAirline)
        )

    @override
    def merge_attrs(self, ctx: AirContext, other: Self):
        self.codes.update(other.codes)

    @override
    def merge_key(self, ctx: AirContext) -> str:
        return self.get_one(ctx, AirAirline).merge_key(ctx)

    @override
    def prepare_export(self, ctx: AirContext):
        self.gates = self.get_all_id(ctx, AirGate)

    @override
    def ref(self, ctx: AirContext) -> NodeRef[Self]:
        return NodeRef(AirFlight, codes=self.codes, airline=self.get_one(ctx, AirAirline).name)

    def update(self, ctx: AirContext):
        processed_gates: list[AirGate] = []
        gates = list(self.get_all(ctx, AirGate))
        for gate in gates:
            if (
                existing := next(
                    (
                        a
                        for a in processed_gates
                        if a.get_one(ctx, AirAirport).equivalent(ctx, gate.get_one(ctx, AirAirport))
                    ),
                    None,
                )
            ) is None:
                processed_gates.append(gate)
            elif existing.code is None and gate.code is not None:
                processed_gates.remove(existing)
                self.disconnect(ctx, existing)
                processed_gates.append(gate)
            elif existing.code is not None and gate.code is None:
                self.disconnect(ctx, gate)
            elif existing.code == gate.code:
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
class AirAirport(LocatedNode[_AirContext]):
    acceptable_list_node_types = lambda: (AirGate, AirAirport, LocatedNode)  # noqa: E731

    code: str
    """Unique 3 (sometimes 4)-letter code"""
    name: Sourced[str] | None = None
    """Name of the airport"""
    link: Sourced[str] | None = None
    """Link to the MRT Wiki page for the airport"""

    gates: list[Sourced[int]] = None
    """List of IDs of :py:class:`AirGate` s"""

    @override
    def __init__(
        self,
        ctx: AirContext,
        *,
        code: str,
        name: str | None = None,
        link: str | None = None,
        gates: Iterable[AirGate] | None = None,
        world: Literal["New", "Old"] | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        super().__init__(ctx, world=world, coordinates=coordinates)
        self.code = code
        if name is not None:
            self.name = ctx.source(name)
        if link is not None:
            self.link = ctx.source(link)
        if gates is not None:
            for gate in gates:
                self.connect(ctx, gate, ctx.source(None))

    @override
    def str_ctx(self, ctx: AirContext) -> str:
        return self.code

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        return self.code == other.code

    @override
    def merge_attrs(self, ctx: AirContext, other: Self):
        super().merge_attrs(ctx, other)
        self._merge_sourced(ctx, other, "name")
        self._merge_sourced(ctx, other, "link")

    @override
    def merge_key(self, ctx: AirContext) -> str:
        return self.code

    @override
    def prepare_export(self, ctx: AirContext):
        super().prepare_export(ctx)
        self.gates = self.get_all_id(ctx, AirGate)

    @override
    def ref(self, ctx: AirContext) -> NodeRef[Self]:
        return NodeRef(AirAirport, code=self.code)

    def update(self, ctx: AirContext):
        if (none_gate := next((a for a in self.get_all(ctx, AirGate) if a.code is None), None)) is None:
            return
        for flight in list(none_gate.get_all(ctx, AirFlight)):
            possible_gates = []
            for possible_gate in self.get_all(ctx, AirGate):
                if possible_gate.code is None:
                    continue
                if (airline := possible_gate.get_one(ctx, AirAirline)) is None:
                    continue
                if airline.equivalent(ctx, flight.get_one(ctx, AirAirline)):
                    possible_gates.append(possible_gate)
            if len(possible_gates) == 1:
                new_gate = possible_gates[0]
                sources = {s for a in none_gate.get_edges(ctx, flight) for s in a.s} | {
                    s for a in new_gate.get_edges(ctx, flight) for s in a.s
                }
                flight.disconnect(ctx, none_gate)
                flight.connect(ctx, new_gate, Sourced(None, sources))

    @staticmethod
    @override
    def process_code[T: (str, None)](s: T) -> T:
        if s is None:
            return None
        s = str(s).upper()
        s = AIRPORT_ALIASES.get(s.strip(), s)
        if len(s) == 4 and s[3] == "T":  # noqa: PLR2004
            return s[:3]
        return s


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class AirGate(Node[_AirContext]):
    acceptable_list_node_types = lambda: (AirFlight,)  # noqa: E731
    acceptable_single_node_types = lambda: (AirAirport, AirAirline)  # noqa: E731

    code: str | None
    """Unique gate code. If ``None``, all flights under this gate do not have gate information at this airport"""
    size: Sourced[str] | None = None
    """Abbreviated size of the gate (eg. ``S``, ``M``)"""

    flights: list[Sourced[int]] = None
    """List of IDs of :py:class:`AirFlight` s that stop at this gate. If ``code==None``, all flights under this gate do not have gate information at this airport"""
    airport: Sourced[int] = None
    """ID of the :py:class:`AirAirport`"""
    airline: Sourced[int] | None = None
    """ID of the :py:class:`AirAirline` that owns the gate"""

    @override
    def __init__(
        self,
        ctx: AirContext,
        *,
        code: str | None,
        airport: AirAirport,
        size: str | None = None,
        flights: Iterable[AirFlight] | None = None,
        airline: AirAirline | None = None,
    ):
        super().__init__(ctx)
        self.code = code
        self.connect_one(ctx, airport, ctx.source(None))
        if size is not None:
            self.size = ctx.source(size)
        if flights is not None:
            for flight in flights:
                self.connect(ctx, flight, ctx.source(None))
        if airline is not None:
            self.connect_one(ctx, airline, ctx.source(None))

    @override
    def str_ctx(self, ctx: AirContext) -> str:
        airport = self.get_one(ctx, AirAirport).code
        code = self.code
        return f"{airport} {code}"

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, AirAirport).equivalent(ctx, other.get_one(ctx, AirAirport))

    @override
    def merge_key(self, ctx: AirContext) -> str:
        return self.code

    @override
    def prepare_export(self, ctx: AirContext):
        self.flights = self.get_all_id(ctx, AirFlight)
        self.airport = self.get_one_id(ctx, AirAirport)
        self.airline = self.get_one_id(ctx, AirAirline)

    @override
    def ref(self, ctx: AirContext) -> NodeRef[Self]:
        return NodeRef(AirGate, code=self.code, airport=self.get_one(ctx, AirAirport).code)


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class AirAirline(Node[_AirContext]):
    acceptable_list_node_types = lambda: (AirFlight,)  # noqa: E731

    name: str
    """Name of the airline"""
    link: Sourced[str] | None = None
    """Link to the MRT Wiki page for the airline"""

    flights: list[Sourced[int]] | None = None
    """List of IDs of all :py:class:`AirFlight` s the airline operates"""

    @override
    def __init__(
        self, ctx: AirContext, *, name: str, link: str | None = None, flights: Iterable[AirFlight] | None = None
    ):
        super().__init__(ctx)
        self.name = name
        if link is not None:
            self.link = ctx.source(link)
        if flights is not None:
            for flight in flights:
                self.connect(ctx, flight, ctx.source(None))

    @override
    def str_ctx(self, ctx: AirContext) -> str:
        return self.name

    @override
    def equivalent(self, ctx: AirContext, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: AirContext, other: Self):
        self._merge_sourced(ctx, other, "link")

    @override
    def merge_key(self, ctx: AirContext) -> str:
        return self.name

    @override
    def prepare_export(self, ctx: AirContext):
        self.flights = self.get_all_id(ctx, AirFlight)

    @override
    def ref(self, ctx: AirContext) -> NodeRef[Self]:
        return NodeRef(AirAirline, name=self.name)

    @staticmethod
    def process_airline_name[T: (str, None)](s: T) -> T:
        if s is None:
            return None
        return AIRLINE_ALIASES.get(str(s).strip(), str(s))


class AirContext(_AirContext):
    def update(self):
        for node in track(self.g.nodes(), description=INFO1 + "Updating air nodes"):
            if isinstance(node, AirFlight | AirAirport):
                node.update(self)


type AirSource = AirContext
