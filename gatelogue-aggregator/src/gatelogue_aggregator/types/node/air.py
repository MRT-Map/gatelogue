from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self, override

from gatelogue_aggregator.logging import INFO2, track
from gatelogue_aggregator.sources.air.hardcode import AIRLINE_ALIASES, AIRPORT_ALIASES, DIRECTIONAL_FLIGHT_AIRLINES
from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef, World
from gatelogue_aggregator.types.source import Source, Sourced

if TYPE_CHECKING:
    from collections.abc import Iterable


class AirSource(BaseContext, Source):
    def update(self):
        for node in track(self.g.nodes(), description=INFO2 + "Updating air nodes", remove=False):
            if isinstance(node, AirFlight | AirAirport):
                node.update(self)


class AirFlight(Node[AirSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (AirGate,)
    acceptable_single_node_types: ClassVar = lambda: (AirAirline,)

    codes: set[str]
    """Unique flight code(s). **2-letter airline prefix not included**"""
    mode: Sourced[Literal["helicopter", "seaplane", "warp plane", "traincarts plane"]] | None = None
    """Type of air vehicle or technology used on the flight"""

    # noinspection PyDataclass
    gates: list[Sourced[int]] = None
    """List of IDs of :py:class:`AirGate` s that the flight goes to. Should be of length 2 in most cases"""
    airline: Sourced[int] = None
    """ID of the :py:class:`AirAirline` the flight is operated by"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: AirSource,
        *,
        codes: set[str],
        airline: AirAirline,
        mode: Literal["helicopter", "seaplane", "warp plane", "traincarts plane"] | None = None,
        gates: Iterable[AirGate] | None = None,
    ):
        self = super().new(ctx, codes=codes)
        self.connect_one(ctx, airline)
        if mode is not None:
            self.mode = ctx.source(mode)
        if gates is not None:
            for gate in gates:
                self.connect(ctx, gate)
        return self

    @override
    def str_ctx(self, ctx: AirSource) -> str:
        airline_name = self.get_one(ctx, AirAirline).name
        code = "/".join(self.codes)
        return f"{airline_name} {code}"

    @override
    def equivalent(self, ctx: AirSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, AirAirline).equivalent(
            ctx, other.get_one(ctx, AirAirline)
        )

    @override
    def merge_attrs(self, ctx: AirSource, other: Self):
        self.codes.update(other.codes)

    @override
    def merge_key(self, ctx: AirSource) -> str:
        return self.get_one(ctx, AirAirline).merge_key(ctx)

    @override
    def prepare_merge(self):
        self.codes = {str(a).strip() for a in self.codes}
        if self.mode is not None:
            self.mode.v = str(self.mode.v).strip()

    @override
    def prepare_export(self, ctx: AirSource):
        self.gates = self.get_all_id(ctx, AirGate)
        self.airline = self.get_one_id(ctx, AirAirline)

    @override
    def ref(self, ctx: AirSource) -> NodeRef[Self]:
        self.prepare_merge()
        return NodeRef(AirFlight, codes=self.codes, airline=self.get_one(ctx, AirAirline).name)

    def update(self, ctx: AirSource):
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


class AirAirport(LocatedNode[AirSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (AirGate, AirAirport, LocatedNode)

    code: str
    """Unique 3 (sometimes 4)-letter code"""
    name: Sourced[str] | None = None
    """Name of the airport"""
    link: Sourced[str] | None = None
    """Link to the MRT Wiki page for the airport"""

    gates: list[Sourced[int]] = None
    """List of IDs of :py:class:`AirGate` s"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: AirSource,
        *,
        code: str,
        name: str | None = None,
        link: str | None = None,
        gates: Iterable[AirGate] | None = None,
        world: World | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        self = super().new(ctx, code=code, world=world, coordinates=coordinates)
        if name is not None:
            self.name = ctx.source(name)
        if link is not None:
            self.link = ctx.source(link)
        if gates is not None:
            for gate in gates:
                self.connect(ctx, gate)
        return self

    @override
    def str_ctx(self, ctx: AirSource) -> str:
        return self.code

    @override
    def equivalent(self, ctx: AirSource, other: Self) -> bool:
        return self.code == other.code

    @override
    def merge_attrs(self, ctx: AirSource, other: Self):
        super().merge_attrs(ctx, other)
        self._merge_sourced(ctx, other, "name")
        self._merge_sourced(ctx, other, "link")

    @override
    def merge_key(self, ctx: AirSource) -> str:
        return self.code

    @override
    def prepare_merge(self):
        super().prepare_merge()
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.link is not None:
            self.link.v = str(self.link.v).strip()

    @override
    def prepare_export(self, ctx: AirSource):
        super().prepare_export(ctx)
        self.gates = self.get_all_id(ctx, AirGate)

    @override
    def ref(self, ctx: AirSource) -> NodeRef[Self]:
        self.prepare_merge()
        return NodeRef(AirAirport, code=self.code)

    def update(self, ctx: AirSource):
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
                flight.connect(ctx, new_gate, source=sources)

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


class AirGate(Node[AirSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (AirFlight,)
    acceptable_single_node_types: ClassVar = lambda: (AirAirport, AirAirline)

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

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: AirSource,
        *,
        code: str | None,
        airport: AirAirport,
        size: str | None = None,
        flights: Iterable[AirFlight] | None = None,
        airline: AirAirline | None = None,
    ):
        self = super().new(ctx, code=code)
        self.connect_one(ctx, airport)
        if size is not None:
            self.size = ctx.source(size)
        if flights is not None:
            for flight in flights:
                self.connect(ctx, flight)
        if airline is not None:
            self.connect_one(ctx, airline)
        return self

    @override
    def str_ctx(self, ctx: AirSource) -> str:
        airport = self.get_one(ctx, AirAirport).code
        code = self.code
        return f"{airport} {code}"

    @override
    def equivalent(self, ctx: AirSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, AirAirport).equivalent(ctx, other.get_one(ctx, AirAirport))

    @override
    def merge_attrs(self, ctx: AirSource, other: Self):
        self._merge_sourced(ctx, other, "size")

    @override
    def merge_key(self, ctx: AirSource) -> str:
        return self.code

    @override
    def prepare_merge(self):
        if self.code is not None:
            self.code = str(self.code).strip()
        if self.size is not None:
            self.size.v = str(self.size.v).strip()

    @override
    def prepare_export(self, ctx: AirSource):
        self.flights = self.get_all_id(ctx, AirFlight)
        self.airport = self.get_one_id(ctx, AirAirport)
        self.airline = self.get_one_id(ctx, AirAirline)

    @override
    def ref(self, ctx: AirSource) -> NodeRef[Self]:
        self.prepare_merge()
        return NodeRef(AirGate, code=self.code, airport=self.get_one(ctx, AirAirport).code)


class AirAirline(Node[AirSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (AirFlight,)

    name: str
    """Name of the airline"""
    link: Sourced[str] | None = None
    """Link to the MRT Wiki page for the airline"""

    flights: list[Sourced[int]] | None = None
    """List of IDs of all :py:class:`AirFlight` s the airline operates"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, ctx: AirSource, *, name: str, link: str | None = None, flights: Iterable[AirFlight] | None = None):
        self = super().new(ctx, name=name)
        if link is not None:
            self.link = ctx.source(link)
        if flights is not None:
            for flight in flights:
                self.connect(ctx, flight)
        return self

    @override
    def str_ctx(self, ctx: AirSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: AirSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: AirSource, other: Self):
        self._merge_sourced(ctx, other, "link")

    @override
    def merge_key(self, ctx: AirSource) -> str:
        return self.name

    @override
    def prepare_merge(self):
        self.name = str(self.name).strip()
        if self.link is not None:
            self.link.v = str(self.link.v).strip()

    @override
    def prepare_export(self, ctx: AirSource):
        self.flights = self.get_all_id(ctx, AirFlight)

    @override
    def ref(self, ctx: AirSource) -> NodeRef[Self]:
        self.prepare_merge()
        return NodeRef(AirAirline, name=self.name)

    @staticmethod
    def process_airline_name[T: (str, None)](s: T) -> T:
        if s is None:
            return None
        return AIRLINE_ALIASES.get(str(s).strip(), str(s))
