from __future__ import annotations

import re
from re import Pattern
from typing import TYPE_CHECKING, Callable

import rich.progress

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.types.air import AirContext, Airport
from gatelogue_aggregator.types.base import Source, Sourced

if TYPE_CHECKING:
    from pathlib import Path

_EXTRACTORS: list[Callable[[WikiAirport, Path, int], None]] = []


@_EXTRACTORS.append
def pce(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Peacopolis International Airport",
        "PCE",
        re.compile(r"\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]].*?|)\|\|.*Service"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def mwt(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Miu Wan Tseng Tsz Leng International Airport",
        "MWT",
        re.compile(r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|\n)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def kek(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Kazeshima Eumi Konaejima Airport",
        "KEK",
        re.compile(r"\|(?P<code>[^|}]*?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)\|\|"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def lar(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Larkspur Lilyflower International Airport",
        "LAR",
        re.compile(r"(?s)'''(?P<code>[^|]*?)'''\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)\|\|.*?status"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def abg(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Antioch-Bay Point Garvey International Airport",
        "ABG",
        re.compile(
            r"\|(?P<code>.*?\d)\|\| ?(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)(?:\|\||\n)",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def opa(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Oparia LeTourneau International Airport",
        "OPA",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def chb(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Chan Bay Municipal Airport",
        "CHB",
        re.compile(
            r"\|Gate (?P<code>.*?)\n\|.\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def cbz(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Chan Bay Zeta Airport",
        "CBZ",
        re.compile(r"\|(?P<code>[AB]\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def cbi(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Chan Bay International Airport",
        "CBI",
        re.compile(r"\|(?P<code>\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def dje(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Deadbush Johnston-Euphorial Airport",
        "DJE",
        re.compile(r"\|(?P<code>\d+?)\n\| (?:(?P<airline>[^\n<]*)|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def vda(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Deadbush Valletta Desert Airport",
        "VDA",
        re.compile(r"\|(?P<code>\d+?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def wmi(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "West Mesa International Airport",
        "WMI",
        re.compile(r"\|Gate (?P<code>.*?)\n\| (?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def dfm(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Deadbush Foxfoe Memorial Airport",
        "DFM",
        re.compile(
            r"\|Gate (?P<code>.*?)\n\|(?P<size>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def gsm(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Gemstride Melodia Airfield",
        "GSM",
        re.compile(
            r"\|(?P<code>.*?)\n\|'''(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>[^N]\S[^|]*)|[^|]*?)'''"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def vfw(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "Venceslo-Fifth Ward International Airport",
        "VFW",
        re.compile(
            r"\|-\n\|(?P<code>\w\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def sdz(ctx: WikiAirport, cache_dir, timeout):
    ctx.extract_airport(
        "San Dzobiak International Airport",
        "SDZ",
        re.compile(
            r"\|-\n\|(?P<code>\w\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)",
            re.MULTILINE,
        ),
        cache_dir,
        timeout,
    )


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

    def extract_airport(
        self,
        page_name: str,
        airport_code: str,
        regex: Pattern[str],
        cache_dir: Path = DEFAULT_CACHE_DIR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Airport:
        wikitext = get_wiki_text(page_name, cache_dir, timeout)
        pos = 0
        airport = self.get_airport(code=airport_code, link=Sourced(get_wiki_link(page_name)).source(self))
        while (match := regex.search(wikitext, pos)) is not None:
            pos = match.start() + 1
            captures = match.groupdict()
            self.get_gate(
                code=captures["code"],
                airport=airport.source(self),
                size=Sourced(captures["size"]).source(self) if "size" in captures else None,
            )
        if pos == 0:
            rich.print(f"[red]Extraction for {airport_code} yielded no results")
        return airport
