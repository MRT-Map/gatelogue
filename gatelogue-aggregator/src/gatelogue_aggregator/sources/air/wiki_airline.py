from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

from gatelogue_aggregator.source import AirSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text


if TYPE_CHECKING:

    from gatelogue_aggregator.config import Config


class _NameDescriptor:
    def __get__(self, instance: None, owner: type[RegexWikiAirline]):
        return f"MRT Wiki (Airline {owner.airline_name})"


class RegexWikiAirline(AirSource):
    name = _NameDescriptor()
    text: str
    airline_name: ClassVar[str]
    page_name: ClassVar[str]
    regex: ClassVar[re.Pattern[str]]

    def prepare(self, config: Config):
        self.text = get_wiki_text(self.page_name, config)

    def build(self, config: Config):
        airline = self.airline(name=self.airline_name, link=get_wiki_link(self.page_name))
        for match in re.finditer(self.regex, self.text):
            matches: dict[str, str] = match.groupdict()
            flight_code = matches["code"]
            size = matches.get("size") or self.size(matches)

            airport1_code = matches.get("a1") or matches.get("a12")
            airport1_name = matches.get("n1")
            if airport1_code is None and airport1_name is None:
                msg = "Provide either code or name for airport 1"
                raise ValueError(msg)
            gate1_code = matches.get("g1")
            if airport1_code is not None:
                self.process_airport_code(airport1_code)
            if airport1_name is not None:
                self.process_airport_name(airport1_name)
            if gate1_code is not None:
                self.process_airport_gate_code(gate1_code, airport1_code)
            airport1 = self.airport(code=airport1_code, names=None if airport1_name is None else {airport1_name})
            gate1 = self.gate(code=gate1_code, airport=airport1, size=size, airline=airline)

            airport2_code = matches.get("a2") or matches.get("a22")
            airport2_name = matches.get("n2")
            if airport2_code is None and airport2_name is None:
                msg = "Provide either code or name for airport 2"
                raise ValueError(msg)
            gate2_code = matches.get("g2")
            if airport2_code is not None:
                self.process_airport_code(airport2_code)
            if airport2_name is not None:
                self.process_airport_name(airport2_name)
            if gate2_code is not None:
                self.process_airport_gate_code(gate2_code, airport2_code)
            airport2 = self.airport(code=airport2_code, names=None if airport2_name is None else {airport2_name})
            gate2 = self.gate(code=gate2_code, airport=airport2, size=size, airline=airline)

            self.flight(airline=airline, code=flight_code, from_=gate1, to=gate2)
            self.flight(airline=airline, code=self.process_flight_code_back(flight_code), from_=gate2, to=gate1)

            airport3_code = matches.get("a3") or matches.get("a32")
            airport3_name = matches.get("n3")
            if airport3_code is None and airport3_name is None:
                continue
            gate3_code = matches.get("g3")
            if airport3_code is not None:
                self.process_airport_code(airport3_code)
            if airport3_name is not None:
                self.process_airport_name(airport3_name)
            if gate3_code is not None:
                self.process_airport_gate_code(gate3_code, airport3_code)
            airport3 = self.airport(code=airport3_code, names=None if airport3_name is None else {airport3_name})
            gate3 = self.gate(code=gate3_code, airport=airport3, size=size, airline=airline)
            self.flight(airline=airline, code=flight_code, from_=gate1, to=gate3)
            self.flight(airline=airline, code=flight_code, from_=gate3, to=gate1)
            self.flight(airline=airline, code=flight_code, from_=gate2, to=gate3)
            self.flight(airline=airline, code=flight_code, from_=gate3, to=gate2)

    @staticmethod
    def size(_matches: dict[str, str]) -> str | None:
        return None

    @staticmethod
    def process_airport_code(code: str) -> str:
        return code

    @staticmethod
    def process_airport_name(name: str) -> str:
        return name

    @staticmethod
    def process_airport_gate_code(gate: str, _airport: str) -> str:
        return gate

    @staticmethod
    def process_flight_code_back(code: str) -> str:
        return code
