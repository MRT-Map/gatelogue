from __future__ import annotations

from typing import TYPE_CHECKING

import rich.progress

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import INFO2, ERROR, PROGRESS, RESULT
from gatelogue_aggregator.sources.air.wiki_extractors.airport import _EXTRACTORS
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.air import AirContext, Airline, Airport, AirSource, Gate
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from pathlib import Path
    from re import Pattern


class WikiAirport(AirSource):
    name = "MRT Wiki (Airport)"
    priority = 3

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        AirContext.__init__(self)
        Source.__init__(self)
        for airline in PROGRESS.track(_EXTRACTORS, description=INFO2 + "Extracting data from wikipages"):
            airline(self, cache_dir, timeout)

    def regex_extract_airport(
        self,
        page_name: str,
        airport_code: str,
        regex: Pattern[str],
        cache_dir: Path = DEFAULT_CACHE_DIR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Airport:
        wikitext = get_wiki_text(page_name, cache_dir, timeout)
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
        return self.airport(code=Airport.process_code(airport_code), link=get_wiki_link(page_name))

    def extract_get_gate(
        self,
        airport: Airport,
        code: str,
        size: str | None = None,
        airline: str | None = None,
        airline2: str | None = None,
        **_,
    ) -> Gate:
        airline = Airline.process_airline_name(airline or airline2)
        g = self.gate(
            code=Gate.process_code(code),
            airport=airport,
            size=str(size) if size is not None else None,
        )
        if airline is not None:
            g.connect_one(self, self.airline(name=airline))
        return g
