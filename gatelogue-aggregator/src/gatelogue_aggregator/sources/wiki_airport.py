from __future__ import annotations

from typing import TYPE_CHECKING

import rich.progress

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.sources.wiki_extractors.airport import _EXTRACTORS
from gatelogue_aggregator.types.air import AirContext, Airport, Gate
from gatelogue_aggregator.types.base import Source, Sourced, process_airport_code, process_code, search_all

if TYPE_CHECKING:
    from pathlib import Path
    from re import Pattern


class WikiAirport(AirContext, Source):
    name = "MRT Wiki"

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        AirContext.__init__(self)
        Source.__init__(self)
        for i, airline in enumerate(_EXTRACTORS):
            rich.print(f"[green]  Extracting data from wikipages ({i + 1}/{len(_EXTRACTORS)})")
            airline(self, cache_dir, timeout)
        rich.print("[green]  Extracted")

        self.update()

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
            rich.print(f"[red]  Extraction for {airport_code} yielded no results")
        else:
            rich.print(f"[green]  {airport_code} has {result} gates")
        return airport

    def extract_get_airport(self, airport_code: str, page_name: str):
        return self.get_airport(
            code=process_airport_code(airport_code), link=Sourced(get_wiki_link(page_name)).source(self)
        )

    def extract_get_gate(
        self,
        airport: Airport,
        code: str,
        size: str | None = None,
        airline: str | None = None,
        airline2: str | None = None,
        **_,
    ) -> Gate:
        airline = airline or airline2
        return self.get_gate(
            code=process_code(code),
            airport=airport.source(self),
            size=Sourced(str(size)).source(self) if size is not None else None,
            airline=self.get_airline(name=airline).source(self) if airline is not None else None,
        )
