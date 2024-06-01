from __future__ import annotations

from re import Pattern
from typing import TYPE_CHECKING

import rich.progress

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.sources.wiki_extractors.airline import _EXTRACTORS
from gatelogue_aggregator.types.air import AirContext, Airline, Flight
from gatelogue_aggregator.types.base import Source, Sourced, search_all, process_code, process_airport_code

if TYPE_CHECKING:
    from pathlib import Path


class WikiAirline(AirContext, Source):
    name = "MRT Wiki"

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        AirContext.__init__(self)
        Source.__init__(self)
        for i, airline in enumerate(_EXTRACTORS):
            rich.print(f"[green]  Extracting data from wikipages ({i+1}/{len(_EXTRACTORS)})")
            airline(self, cache_dir, timeout)
        rich.print("[green]  Extracted")

        self.update()

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
        result = False
        for match in search_all(regex, wikitext):
            self.extract_get_flight(airline, **match.groupdict())
            result = True
        if not result:
            rich.print(f"[red]Extraction for {airline_name} yielded no results")
        return airline

    def extract_get_airline(self, airline_name: str, page_name: str) -> Airline:
        return self.get_airline(name=airline_name, link=Sourced(get_wiki_link(page_name)).source(self))

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
        return self.get_flight(
            codes={process_code(code)},
            gates=[
                self.get_gate(
                    code=process_code(g1),
                    size=Sourced(str(s)).source(self) if s is not None else None,
                    airport=self.get_airport(code=process_airport_code(a1)).source(self),
                ).source(self),
                self.get_gate(
                    code=process_code(g2),
                    size=Sourced(str(s)).source(self) if s is not None else None,
                    airport=self.get_airport(code=process_airport_code(a2)).source(self),
                ).source(self),
            ],
            airline=airline.source(self),
        )
