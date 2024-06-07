from __future__ import annotations

from typing import TYPE_CHECKING

import rich.progress

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import ERROR, INFO2, PROGRESS, RESULT
from gatelogue_aggregator.sources.air.wiki_extractors.airline import _EXTRACTORS
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.air import AirContext, Airline, Airport, AirSource, Flight, Gate
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from pathlib import Path
    from re import Pattern


class WikiAirline(AirSource):
    name = "MRT Wiki (Airline)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        AirContext.__init__(self)
        Source.__init__(self)
        for airline in PROGRESS.track(_EXTRACTORS, description=INFO2 + "Extracting data from wikipages"):
            airline(self, cache_dir, timeout)

    def regex_extract_airline(
        self,
        airline_name: str,
        page_name: str,
        regex: Pattern[str],
        cache_dir: Path = DEFAULT_CACHE_DIR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Airline:
        wikitext = get_wiki_text(page_name, cache_dir, timeout)
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

    def extract_get_airline(self, airline_name: str, page_name: str) -> Airline:
        return self.airline(name=Airline.process_airline_name(airline_name), link=get_wiki_link(page_name))

    def extract_get_flight(
        self,
        airline: Airline,
        code: str,
        a1: str,
        a2: str,
        g1: str | None = None,
        g2: str | None = None,
        s: str | None = None,
        **_,
    ) -> Flight:
        f = self.flight(codes=Flight.process_code(code, airline.merged_attr(self, "name")), airline=airline)
        f.connect(
            self,
            self.gate(
                code=Gate.process_code(g1),
                airport=self.airport(code=Airport.process_code(a1)),
                size=str(s) if s is not None else None,
            ),
        )
        f.connect(
            self,
            self.gate(
                code=Gate.process_code(g2),
                airport=self.airport(code=Airport.process_code(a2)),
                size=str(s) if s is not None else None,
            ),
        )
        return f
