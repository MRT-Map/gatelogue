from __future__ import annotations

from typing import TYPE_CHECKING

import rich.progress

from gatelogue_aggregator.logging import ERROR, INFO2, RESULT, track
from gatelogue_aggregator.sources.air.wiki_extractors.airline import _EXTRACTORS
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.types.node.air import AirAirline, AirAirport, AirContext, AirFlight, AirGate, AirSource
from gatelogue_aggregator.types.source import Source
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from re import Pattern

    from gatelogue_aggregator.types.config import Config


class WikiAirline(AirSource):
    name = "MRT Wiki (Airline)"
    priority = 1

    def __init__(self, config: Config):
        AirContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return
        for airline in track(_EXTRACTORS, description=INFO2 + "Extracting data from wikipages"):
            airline(self, config)
        self.save_to_cache(config, self.g)

    def regex_extract_airline(
        self,
        airline_name: str,
        page_name: str,
        regex: Pattern[str],
        config: Config,
    ) -> AirAirline:
        wikitext = get_wiki_text(page_name, config)
        airline = self.extract_get_airline(airline_name, page_name)
        result = 0
        for match in search_all(regex, wikitext):
            self.extract_get_flight(airline, **match.groupdict())
            result += 1
        if not result:
            rich.print(ERROR + f"Extraction for {airline_name} yielded no results")
        else:
            rich.print(RESULT + f"{airline_name} has {result} flights")
        return airline

    def extract_get_airline(self, airline_name: str, page_name: str) -> AirAirline:
        return self.air_airline(name=AirAirline.process_airline_name(airline_name), link=get_wiki_link(page_name))

    def extract_get_flight(
        self,
        airline: AirAirline,
        code: str,
        a1: str,
        a2: str,
        g1: str | None = None,
        g2: str | None = None,
        s: str | None = None,
        **_,
    ) -> AirFlight:
        f = self.air_flight(codes=AirFlight.process_code(code, airline.merged_attr(self, "name")), airline=airline)
        f.connect(
            self,
            self.air_gate(
                code=AirGate.process_code(g1),
                airport=self.air_airport(code=AirAirport.process_code(a1)),
                size=str(s) if s is not None else None,
            ),
        )
        f.connect(
            self,
            self.air_gate(
                code=AirGate.process_code(g2),
                airport=self.air_airport(code=AirAirport.process_code(a2)),
                size=str(s) if s is not None else None,
            ),
        )
        return f
