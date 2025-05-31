from __future__ import annotations

from typing import TYPE_CHECKING, override

from gatelogue_aggregator.logging import INFO2, track
from gatelogue_aggregator.sources.air.wiki_extractors.airport import _EXTRACTORS
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.types.node.air import AirAirline, AirAirport, AirGate, AirSource
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from collections.abc import Callable
    from re import Pattern

    from gatelogue_aggregator.types.config import Config
    from gatelogue_aggregator.types.node.base import Node


class WikiAirport(AirSource):
    name = "MRT Wiki (Airport)"
    priority = 3

    @classmethod
    @override
    def reported_nodes(cls) -> tuple[type[Node], ...]:
        return (AirAirport,)

    def build(self, config: Config):
        for airline in track(_EXTRACTORS, INFO2, description="Extracting data from wikipages"):
            airline(self, config)

    def regex_extract_airport(
        self,
        page_name: str,
        airport_code: str,
        regex: Pattern[str],
        config: Config,
        size: str | Callable[[dict[str, str]], str] | None = None,
    ) -> AirAirport:
        wikitext = get_wiki_text(page_name, config)
        airport = self.extract_get_airport(airport_code, page_name)
        for match in search_all(regex, wikitext):
            matches = match.groupdict()
            if size is not None:
                matches["size"] = size if isinstance(size, str) else size(matches)
            self.extract_get_gate(airport, **matches)
        return airport

    def extract_get_airport(self, airport_code: str, page_name: str):
        return AirAirport.new(self, code=AirAirport.process_code(airport_code), link=get_wiki_link(page_name))

    def extract_get_gate(
        self,
        airport: AirAirport,
        *,
        code: str,
        size: str | None = None,
        airline: str | None = None,
        airline2: str | None = None,
        **_,
    ) -> AirGate:
        airline = AirAirline.process_airline_name(airline or airline2)
        g = AirGate.new(
            self,
            code=AirGate.process_code(code, airline, airport.code),
            airport=airport,
            size=str(size) if size is not None else None,
        )
        if airline is not None:
            g.connect_one(self, AirAirline.new(self, name=airline), self.source(None))
        return g
