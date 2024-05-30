from __future__ import annotations

import re
from pathlib import Path
from re import Pattern
from typing import Callable

import rich.progress

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.wiki_base import get_wikitext
from gatelogue_aggregator.types.air import Airline
from gatelogue_aggregator.types.base import Source, Sourced
from gatelogue_aggregator.types.context import AirContext

_EXTRACTORS: list[Callable[[WikiAirline, Path, int], ...]] = []


@_EXTRACTORS.append
def astrella(ctx: WikiAirline, cache_dir, timeout):
    ctx.extract_airline(
        "Astrella",
        "Astrella",
        re.compile(
            r"\{\{AstrellaFlight\|code = AA(?P<code>[^$\n]*?)\|airport1 = (?P<a1>[^\n]*?)\|gate1 = (?P<g1>[^\n]*?)\|airport2 = (?P<a2>[^\n]*?)\|gate2 = (?P<g2>[^\n]*?)\|size = (?P<s>[^\n]*?)\|status = active}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def turbula(ctx: WikiAirline, cache_dir, timeout):
    ctx.extract_airline(
        "Turbula",
        "Template:TurbulaFlightList",
        re.compile(
            r"code = LU(?P<code>\d*).*?(?:\n.*?)?airport1 = (?P<a1>.*?) .*?airport2 = (?P<a2>.*?) .*?status = active"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def blu_air(ctx: WikiAirline, cache_dir, timeout):
    ctx.extract_airline(
        "BluAir",
        "List of BluAir flights",
        re.compile(
            r"\{\{BA\|BU(?P<code>.*?)\|(?P<a1>.*?)\|(?P<a2>.*?)\|.*?\|.*?\|(?P<g1>.*?)\|(?P<g2>.*?)\|a\|.*?\|.}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def intra_air(ctx: WikiAirline, cache_dir, timeout):
    ctx.extract_airline(
        "IntraAir",
        "IntraAir/Flight List",
        re.compile(
            r"Flight (?P<code>.*?)}}.*?\n.*?'''(?P<a1>.*?)'''.*?\n.*?'''(?P<a2>.*?)'''.*?\n.*?\n.*?\n.*?open.*?\n.*?\n.*?\n.*?'''(?P<g1>[^']*?)'''\n.*?'''(?P<g2>[^']*?)'''\n"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def fli_high(ctx: WikiAirline, cache_dir, timeout):
    ctx.extract_airline(
        "FliHigh",
        "FliHigh Airlines",
        re.compile(
            r"\{\{FHList\|FH(?P<code>.*?)\|(?P<a1>.*?)\|(?P<a2>.*?)\|.*?\|.*?\|(?P<g1>.*?)\|(?P<g2>.*?)\|a\|.*?\|FH}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def air_mesa(ctx: WikiAirline, cache_dir, timeout):
    ctx.extract_airline(
        "AirMesa",
        "AirMesa",
        re.compile(
            r"\{\{BA\|AM(?P<code>.*?)\|(?P<a1>.*?)\|(?P<a2>.*?)\|.*?\|.*?\|(?P<g1>.*?)\|(?P<g2>.*?)\|a\|.*?\|..}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def air(ctx: WikiAirline, cache_dir, timeout):
    ctx.extract_airline(
        "Air",
        "Template:Air",
        re.compile(
            r"\{\{BA\|↑↑(?P<code>.*?)\|(?P<a1>.*?)\|(?P<a2>.*?)\|.*?\|.*?\|(?P<g1>.*?)\|(?P<g2>.*?)\|a\|.*?\|..}}"
        ),
        cache_dir,
        timeout,
    )


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

    def extract_airline(
        self,
        airline_name: str,
        page_name: str,
        regex: Pattern[str],
        cache_dir: Path = DEFAULT_CACHE_DIR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Airline:
        wikitext = get_wikitext(page_name, cache_dir, timeout)
        pos = 0
        airline = self.get_airline(name=airline_name)
        while (match := regex.search(wikitext, pos)) is not None:
            pos = match.start() + 1
            captures = match.groupdict()
            self.get_flight(
                codes={captures["code"]},
                gates=[
                    self.get_gate(
                        code=captures.get("g1"),
                        size=Sourced(captures["s"]).source(self) if "s" in captures else None,
                        airport=self.get_airport(code=captures["a1"]).source(self),
                    ).source(self),
                    self.get_gate(
                        code=captures.get("g2"),
                        size=Sourced(captures["s"]).source(self) if "s" in captures else None,
                        airport=self.get_airport(code=captures["a2"]).source(self),
                    ).source(self),
                ],
                airline=airline.source(self),
            )
        return airline
