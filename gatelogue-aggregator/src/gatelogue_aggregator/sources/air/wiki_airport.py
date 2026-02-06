from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

from gatelogue_aggregator.source import AirSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text


if TYPE_CHECKING:

    from gatelogue_aggregator.config import Config


class _NameDescriptor:
    def __get__(self, instance: None, owner: type[RegexWikiAirport]):
        return f"MRT Wiki (Airport {owner.airport_code})"


class RegexWikiAirport(AirSource):
    name = _NameDescriptor()
    text: str
    airport_code: ClassVar[str]
    page_name: ClassVar[str]
    regex: ClassVar[re.Pattern[str]]

    def prepare(self, config: Config):
        self.text = get_wiki_text(self.page_name, config)

    def build(self, config: Config):
        airport = self.airport(code=self.airport_code, link=get_wiki_link(self.page_name), names={self.page_name})
        for match in re.finditer(self.regex, self.text):
            matches: dict[str, str] = match.groupdict()
            gate_code = self.process_gate_code(matches["code"])
            size = matches.get("size") or self.size(matches)
            if (airline_name := (matches.get("airline", matches.get("airline2")))) is not None:
                airline = self.airline(name=self.process_airline_name(airline_name))
            else:
                airline = None
            self.gate(code=gate_code, airport=airport, size=size, airline=airline)

    @staticmethod
    def size(_matches: dict[str, str]) -> str | None:
        return None

    @staticmethod
    def process_airline_name(airline_name: str) -> str:
        return airline_name

    @staticmethod
    def process_gate_code(gate_code: str) -> str:
        return gate_code
