from __future__ import annotations

import difflib
import itertools
import re
from typing import TYPE_CHECKING, ClassVar, Self, override

import gatelogue_types as gt

from gatelogue_aggregator.logging import ERROR, INFO2, RESULT, track
from gatelogue_aggregator.sources.air.hardcode import (
    AIRLINE_ALIASES,
    AIRPORT_ALIASES,
    DIRECTIONAL_FLIGHT_AIRLINES,
    GATE_ALIASES,
)
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef
from gatelogue_aggregator.types.source import Source, Sourced

if TYPE_CHECKING:
    from collections.abc import Iterable


class AirSource(Source):
    def update(self):
        for node in track(self.g.nodes(), INFO2, description="Updating air nodes"):
            if isinstance(node, AirFlight | AirAirport):
                node.update(self)


class AirFlight(gt.AirFlight, Node, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (AirGate,)
    acceptable_single_node_types: ClassVar = lambda: (AirAirline,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: AirSource,
        *,
        codes: set[str],
        airline: AirAirline,
        mode: gt.PlaneMode | None = None,
        gates: Iterable[AirGate] | None = None,
    ):
        self = super().new(src, codes=codes)
        self.connect_one(src, airline)
        if mode is not None:
            self.mode = src.source(mode)
        if gates is not None:
            for gate in gates:
                self.connect(src, gate)
        return self

    @override
    def str_src(self, src: AirSource) -> str:
        airline_name = self.get_one(src, AirAirline).name
        code = "/".join(self.codes)
        return f"{airline_name} {code}"

    @override
    def equivalent(self, src: AirSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(src, AirAirline).equivalent(
            src, other.get_one(src, AirAirline)
        )

    @override
    def merge_attrs(self, src: AirSource, other: Self):
        self.codes.update(other.codes)

    @override
    def merge_key(self, src: AirSource) -> str:
        return self.get_one(src, AirAirline).merge_key(src)

    @override
    def sanitise_strings(self):
        self.codes = {str(a).strip() for a in self.codes}
        if self.mode is not None:
            self.mode.v = str(self.mode.v).strip()

    @override
    def export(self, src: AirSource) -> gt.AirFlight:
        return gt.AirFlight(**self._as_dict(src))

    @override
    def _as_dict(self, src: AirSource) -> dict:
        return super()._as_dict(src) | {
            "gates": self.get_all_id(src, AirGate),
            "airline": self.get_one_id(src, AirAirline),
        }

    @override
    def ref(self, src: AirSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(AirFlight, codes=self.codes, airline=self.get_one(src, AirAirline).name)

    @override
    def report(self, src: AirSource):
        pass

    def update(self, src: AirSource):
        processed_gates: list[AirGate] = []
        gates = list(self.get_all(src, AirGate))
        for gate in gates:
            if (
                existing := next(
                    (
                        a
                        for a in processed_gates
                        if a.get_one(src, AirAirport).equivalent(src, gate.get_one(src, AirAirport))
                    ),
                    None,
                )
            ) is None:
                processed_gates.append(gate)
            elif existing.code is None and gate.code is not None:
                processed_gates.remove(existing)
                self.get_edge(src, gate).source(self.get_edge(src, existing))
                self.disconnect(src, existing)
                processed_gates.append(gate)
            elif existing.code is not None and gate.code is None:
                self.get_edge(src, existing).source(self.get_edge(src, gate))
                self.disconnect(src, gate)
            elif existing.code == gate.code:
                existing.merge(src, gate)

        if self.mode is None:
            size = {a.size.v for a in self.get_all(src, AirGate) if a.size is not None}
            sources = set(itertools.chain(*(a.size.s for a in self.get_all(src, AirGate) if a.size is not None)))
            if size == {"SP"}:
                self.mode = Sourced("seaplane", sources)
            elif size == {"H"}:
                self.mode = Sourced("helicopter", sources)
            elif len(size) != 0:
                self.mode = Sourced("warp plane", sources)

    @staticmethod
    def process_code[T: (str, None)](s: T | set[str], airline_name: str | None = None) -> set[T]:
        if isinstance(s, set):
            return {sss for ss in s for sss in AirFlight.process_code(ss, airline_name)}
        s = Node.process_code(s)

        direction_config = DIRECTIONAL_FLIGHT_AIRLINES.get(airline_name)
        if not s.isdigit() or direction_config is None:
            return {s}

        direction = (
            direction_config
            if isinstance(direction_config, str)
            else next(
                (d for r, d in direction_config if r is not None and int(s) in r),
                next((d for r, d in direction_config if r is None), None),
            )
        )
        if direction is None:
            return {s}

        if direction == "odd-even":
            if int(s) % 2 == 1:
                return {s, str(int(s) + 1)}
            return {s, str(int(s) - 1)}
        if int(s) % 2 == 1:
            return {s, str(int(s) - 1)}
        return {s, str(int(s) + 1)}


class AirAirport(gt.AirAirport, LocatedNode, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (AirGate, AirAirport, LocatedNode)
    code: str | None

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: AirSource,
        *,
        code: str | None,
        names: set[str] | None = None,
        link: str | None = None,
        modes: set[gt.PlaneMode] | None = None,
        gates: Iterable[AirGate] | None = None,
        world: gt.World | None = None,
        coordinates: tuple[float, float] | None = None,
    ):
        if code is names is None:
            msg = "`code` and `names` cannot both be `None`"
            raise ValueError(msg)
        self = super().new(src, code=code, world=world, coordinates=coordinates)
        if names is not None:
            self.names = src.source(names)
        if link is not None:
            self.link = src.source(link)
        if modes is not None:
            self.modes = src.source(modes)
        if gates is not None:
            for gate in gates:
                self.connect(src, gate)
        return self

    @override
    def str_src(self, src: AirSource) -> str:
        return self.code or f"`{self.names}`"

    @override
    def equivalent(self, src: AirSource, other: Self) -> bool:
        return (
            (self.code == other.code)
            if None not in (self.code, other.code)
            else len(self.names.v.intersection(other.names.v)) != 0
            if None not in (self.names, other.names)
            else False
        )

    @override
    def merge_attrs(self, src: AirSource, other: Self):
        super().merge_attrs(src, other)
        self._merge_sourced(src, other, "names")
        self._merge_sourced(src, other, "link")
        self._merge_sourced(src, other, "modes")

    @override
    def merge_key(self, src: AirSource) -> str | None:
        return self.code

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        if self.code is not None:
            self.code = str(self.code).strip()
        if self.names is not None:
            self.names.v = {str(a).strip() for a in self.names.v}
        if self.link is not None:
            self.link.v = str(self.link.v).strip()
        if self.modes is not None:
            self.modes.v = {str(a).strip() for a in self.modes.v}

    @override
    def export(self, src: AirSource) -> gt.AirAirport:
        if self.code is None:
            msg = f"`{'`/`'.join(self.names.v)}`: `code` cannot be `None` when exporting"
            raise ValueError(msg)
        return gt.AirAirport(**self._as_dict(src))

    @override
    def _as_dict(self, src: AirSource) -> dict:
        return super()._as_dict(src) | {
            "gates": self.get_all_id(src, AirGate),
        }

    @override
    def ref(self, src: AirSource) -> NodeRef[Self]:
        self.sanitise_strings()
        if self.code is not None:
            return NodeRef(AirAirport, code=self.code)
        return NodeRef(AirAirport, names=self.names)

    @override
    def report(self, src: AirSource):
        super().report(src)
        if src.is_coord_source():
            return
        num_gates = len(list(self.get_all(src, AirGate)))
        colour = ERROR if num_gates == 0 else RESULT
        self.print_report(src, colour, f"has {num_gates} gates")

    def find_equiv_from_name(self, src: AirSource, node_list: list[Node] | None = None) -> Self | None:
        if self.code is not None:
            return None
        other_airports = [
            a
            for a in (node_list or src.g.nodes())
            if isinstance(a, AirAirport) and a is not self and a.code is not None and a.names is not None
        ]
        if not other_airports:
            return None
        if (
            best_name := next(
                iter(
                    difflib.get_close_matches(
                        next(iter(self.names.v)), [b for a in other_airports for b in a.names.v], 1, 0.0
                    )
                ),
                None,
            )
        ) is None:
            return None
        return next(a for a in other_airports if best_name in a.names.v)

    def update(self, src: AirSource):
        if self.names is not None:
            new_names = set()
            for name in sorted(self.names.v, key=len, reverse=True):
                if not any(
                    (
                        name in existing
                        or sorted(re.sub(r"[^\w\s]", "", name).split())
                        == sorted(re.sub(r"[^\w\s]", "", existing).split())
                    )
                    for existing in new_names
                ):
                    new_names.add(name)
            self.names.v = new_names
        if (none_gate := next((a for a in self.get_all(src, AirGate) if a.code is None), None)) is None:
            return
        for flight in list(none_gate.get_all(src, AirFlight)):
            possible_gates = []
            for possible_gate in self.get_all(src, AirGate):
                if possible_gate.code is None:
                    continue
                if (airline := possible_gate.get_one(src, AirAirline)) is None:
                    continue
                if airline.equivalent(src, flight.get_one(src, AirAirline)):
                    possible_gates.append(possible_gate)
            if len(possible_gates) == 1:
                new_gate = possible_gates[0]
                sources = {s for a in none_gate.get_edges(src, flight) for s in a.s} | {
                    s for a in new_gate.get_edges(src, flight) for s in a.s
                }
                flight.disconnect(src, none_gate)
                flight.connect(src, new_gate, source=sources)

        if self.modes is not None and self.modes.v == {"seaplane"}:
            for gate in self.get_all(src, AirGate):
                gate.size = Sourced("SP", self.modes.s)
        if self.modes is not None and self.modes.v == {"helicopter"}:
            for gate in self.get_all(src, AirGate):
                gate.size = Sourced("H", self.modes.s)

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


class AirGate(gt.AirGate, Node, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (AirFlight,)
    acceptable_single_node_types: ClassVar = lambda: (AirAirport, AirAirline)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: AirSource,
        *,
        code: str | None,
        airport: AirAirport,
        size: str | None = None,
        flights: Iterable[AirFlight] | None = None,
        airline: AirAirline | None = None,
    ):
        self = super().new(src, code=code)
        self.connect_one(src, airport)
        if size is not None:
            self.size = src.source(size)
        if flights is not None:
            for flight in flights:
                self.connect(src, flight)
        if airline is not None:
            self.connect_one(src, airline)
        return self

    @override
    def str_src(self, src: AirSource) -> str:
        airport = self.get_one(src, AirAirport).code
        code = self.code
        return f"{airport} {code}"

    @override
    def equivalent(self, src: AirSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(src, AirAirport).equivalent(src, other.get_one(src, AirAirport))

    @override
    def merge_attrs(self, src: AirSource, other: Self):
        self._merge_sourced(src, other, "size")

    @override
    def merge_key(self, src: AirSource) -> str:
        return self.code

    @override
    def sanitise_strings(self):
        if self.code is not None:
            self.code = str(self.code).strip()
        if self.size is not None:
            self.size.v = str(self.size.v).strip()

    @override
    def export(self, src: AirSource) -> gt.AirGate:
        return gt.AirGate(**self._as_dict(src))

    @override
    def _as_dict(self, src: AirSource) -> dict:
        return super()._as_dict(src) | {
            "flights": self.get_all_id(src, AirFlight),
            "airport": self.get_one_id(src, AirAirport),
            "airline": self.get_one_id(src, AirAirline),
        }

    @override
    def ref(self, src: AirSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(AirGate, code=self.code, airport=self.get_one(src, AirAirport).code)

    @override
    def report(self, src: AirSource):
        num_flights = len(list(self.get_all(src, AirFlight)))
        if num_flights > 6 and self.code is not None:  # noqa: PLR2004
            self.print_report(src, ERROR, f"has {num_flights} flights")

    @staticmethod
    def process_code[T: (str, None)](s: T, airline_name: str | None = None, airport_code: str | None = None) -> T:
        s = Node.process_code(s)
        if airport_code in GATE_ALIASES:
            if airline_name is not None:
                s = GATE_ALIASES[airport_code].get((airline_name, s), s)
            s = GATE_ALIASES[airport_code].get(s, s)
        return s


class AirAirline(gt.AirAirline, Node, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (AirFlight, AirGate)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: AirSource,
        *,
        name: str,
        link: str | None = None,
        flights: Iterable[AirFlight] | None = None,
        gates: Iterable[AirGate] | None = None,
    ):
        self = super().new(src, name=name)
        if link is not None:
            self.link = src.source(link)
        if flights is not None:
            for flight in flights:
                self.connect(src, flight)
        if gates is not None:
            for gate in gates:
                self.connect(src, gate)
        return self

    @override
    def str_src(self, src: AirSource) -> str:
        return self.name

    @override
    def equivalent(self, src: AirSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, src: AirSource, other: Self):
        self._merge_sourced(src, other, "link")

    @override
    def merge_key(self, src: AirSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        self.name = str(self.name).strip()
        if self.link is not None:
            self.link.v = str(self.link.v).strip()

    @override
    def export(self, src: AirSource) -> gt.AirAirline:
        return gt.AirAirline(**self._as_dict(src))

    @override
    def _as_dict(self, src: AirSource) -> dict:
        return super()._as_dict(src) | {
            "flights": self.get_all_id(src, AirFlight),
            "gates": self.get_all_id(src, AirGate),
        }

    @override
    def ref(self, src: AirSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(AirAirline, name=self.name)

    @override
    def report(self, src: AirSource):
        from gatelogue_aggregator.sources.air.mrt_transit import MRTTransit
        from gatelogue_aggregator.sources.air.wiki_airline import WikiAirline

        num_flights = len(list(self.get_all(src, AirFlight)))
        num_gates = len(list(self.get_all(src, AirGate)))
        colour = (
            ERROR if num_flights == 0 or (num_gates == 0 and not isinstance(src, WikiAirline | MRTTransit)) else RESULT
        )
        self.print_report(src, colour, f"has {num_flights} flights and {num_gates} gates")

    @staticmethod
    def process_airline_name[T: (str, None)](s: T) -> T:
        if s is None:
            return None
        return AIRLINE_ALIASES.get(str(s).strip(), str(s))
