from __future__ import annotations

from typing import TYPE_CHECKING

import rich.progress

from gatelogue_aggregator.logging import ERROR, INFO2, RESULT, track
from gatelogue_aggregator.sources.air.wiki_extractors.airport import _EXTRACTORS
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.types.node.air import AirAirline, AirAirport, AirGate, AirSource
from gatelogue_aggregator.types.source import Source
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from re import Pattern

    from gatelogue_aggregator.types.config import Config


class WikiAirport(AirSource):
    name = "MRT Wiki (Airport)"
    priority = 3

    def __init__(self, config: Config):
        AirSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return
        for airline in track(_EXTRACTORS, description=INFO2 + "Extracting data from wikipages"):
            airline(self, config)
        self.save_to_cache(config, self.g)

    def regex_extract_airport(
        self,
        page_name: str,
        airport_code: str,
        regex: Pattern[str],
        config: Config,
    ) -> AirAirport:
        wikitext = get_wiki_text(page_name, config)
        airport = self.extract_get_airport(airport_code, page_name)
        result = 0
        for match in search_all(regex, wikitext):
            self.extract_get_gate(airport, **match.groupdict())
            result += 1
        if not result:
            rich.print(ERROR + f"Extraction for {airport_code} yielded no results")
        else:
            rich.print(RESULT + f"{airport_code} has {result} gates")
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
