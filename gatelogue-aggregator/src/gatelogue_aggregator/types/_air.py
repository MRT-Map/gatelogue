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


# AirFlight
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


## AirAirport
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
                    or sorted(re.sub(r"[^\w\s]", "", name).split()) == sorted(re.sub(r"[^\w\s]", "", existing).split())
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
