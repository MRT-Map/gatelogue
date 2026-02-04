from __future__ import annotations

import re
from typing import TYPE_CHECKING, override

from gatelogue_aggregator.logging import INFO2, track
from gatelogue_aggregator.source import AirSource
from gatelogue_aggregator.sources.air.wiki_extractors.airline import _EXTRACTORS
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from collections.abc import Callable
    from re import Pattern

    from gatelogue_aggregator.config import Config

class RegexWikiAirline(AirSource):
    # priority = 1
    text: str
    airline_name: str
    page_name: str
    regex: re.Pattern[str]

    def prepare(self, config: Config):
        self.text = get_wiki_text(self.page_name, config)

    def build(self, config: Config):
        airline = self.airline(name=self.airline_name, link=get_wiki_link(self.page_name))
        for match in search_all(self.regex, self.text):
            matches: dict[str, str] = match.groupdict()
            code = matches["code"]
            size = matches.get("size") or self.size(matches)

            code1 = matches.get("a1", matches.get("a12"))
            name1 = matches.get("n1")
            if code1 is None and name1 is None:
                msg = "Provide either code or name for airport 1"
                raise ValueError(msg)
            gate1_code = matches.get("g1")
            if code1 is not None:
                self.process_airport_code(code1)
            if name1 is not None:
                self.process_airport_name(name1)
            if gate1_code is not None:
                self.process_airport_gate_code(gate1_code, code1)
            airport1 = self.airport(code=code1, names={name1})
            gate1 = self.gate(
                code=gate1_code,
                airport=airport1,
                size=size,
                airline=airline
            )

            code2 = matches.get("a2", matches.get("a22"))
            name2 = matches.get("n2")
            if code2 is None and name2 is None:
                msg = "Provide either code or name for airport 2"
                raise ValueError(msg)
            gate2_code = matches.get("g2")
            if code2 is not None:
                self.process_airport_code(code2)
            if name2 is not None:
                self.process_airport_name(name2)
            if gate2_code is not None:
                self.process_airport_gate_code(gate2_code, code2)
            airport2 = self.airport(code=code2, names={name2})
            gate2 = self.gate(
                code=gate2_code,
                airport=airport2,
                size=size,
                airline=airline
            )

            self.flight(airline=airline, code=code, from_=gate1, to=gate2)
            self.flight(airline=airline, code=code, from_=gate2, to=gate1)

            code3 = matches.get("a3", matches.get("a32"))
            name3 = matches.get("n3")
            if code3 is None and name3 is None:
                continue
            gate3_code = matches.get("g3")
            if code3 is not None:
                self.process_airport_code(code3)
            if name3 is not None:
                self.process_airport_name(name3)
            if gate3_code is not None:
                self.process_airport_gate_code(gate3_code, code3)
            airport3 = self.airport(code=code3, names={name3})
            gate3 = self.gate(
                code=gate3_code,
                airport=airport3,
                size=size,
                airline=airline
            )
            self.flight(airline=airline, code=code, from_=gate1, to=gate3)
            self.flight(airline=airline, code=code, from_=gate3, to=gate1)
            self.flight(airline=airline, code=code, from_=gate2, to=gate3)
            self.flight(airline=airline, code=code, from_=gate3, to=gate2)

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
