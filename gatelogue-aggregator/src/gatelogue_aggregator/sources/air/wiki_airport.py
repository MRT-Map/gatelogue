from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

from gatelogue_aggregator.downloader import get_wiki_link, get_wiki_text
from gatelogue_aggregator.source import AirSource

if TYPE_CHECKING:
    from gatelogue_aggregator.config import Config
    import gatelogue_types as gt


class _NameDescriptor:
    def __get__(self, instance: None, owner: type[RegexWikiAirport]):
        return f"MRT Wiki (Airport {owner.airport_code})"


class RegexWikiAirport(AirSource):
    name = _NameDescriptor()
    text: str
    airport_code: ClassVar[str]
    page_name: ClassVar[str]
    regex: ClassVar[re.Pattern[str]]
    additional_names: ClassVar[set[str]] = set()

    def prepare(self, config: Config):
        self.text = get_wiki_text(self.page_name, config)

    def build(self, config: Config):
        airport = self.airport(
            code=self.airport_code, link=get_wiki_link(self.page_name), names={self.page_name, *self.additional_names}
        )
        for match in re.finditer(self.regex, self.text):
            matches: dict[str, str] = match.groupdict()
            gate_code = self.process_gate_code(matches["code"])
            width = int(matches.get("width")) if matches.get("width") else self.width(matches)
            if (airline_name := (matches.get("airline", matches.get("airline2")))) is not None:
                airline = self.airline(name=self.process_airline_name(airline_name))
            else:
                airline = None
            mode = self.mode(matches)
            self.gate(code=gate_code, airport=airport, width=width, airline=airline, mode=mode)

    @staticmethod
    def width(_matches: dict[str, str]) -> int | None:
        return None

    @staticmethod
    def mode(_matches: dict[str, str]) -> gt.AirMode | None:
        return "warp plane"

    @staticmethod
    def process_airline_name(airline_name: str) -> str:
        return airline_name

    @staticmethod
    def process_gate_code(gate_code: str) -> str:
        return gate_code
