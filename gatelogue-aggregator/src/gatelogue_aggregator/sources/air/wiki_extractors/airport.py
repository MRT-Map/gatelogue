from __future__ import annotations

import re
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.wiki_base import get_wiki_html

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from gatelogue_aggregator.sources.air.wiki_airport import WikiAirport

_EXTRACTORS: list[Callable[[WikiAirport, Path, int], None]] = []


@_EXTRACTORS.append
def pce(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Peacopolis International Airport",
        "PCE",
        re.compile(
            r"(?s)\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*?|)\|\|(?:(?!Service).)*Service"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def mwt(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Miu Wan Tseng Tsz Leng International Airport",
        "MWT",
        re.compile(r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|\n)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def kek(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Kazeshima Eumi Konaejima Airport",
        "KEK",
        re.compile(r"\|(?P<code>[^|}]*?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)\|\|"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def lar(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Larkspur Lilyflower International Airport",
        "LAR",
        re.compile(r"(?s)'''(?P<code>[^|]*?)'''\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^\n]*?)]]|[^|]*?)\|\|.*?status"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def abg(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Antioch-Bay Point Garvey International Airport",
        "ABG",
        re.compile(
            r"\|(?P<code>.*?\d)\|\| ?(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)(?:\|\||\n)",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def opa(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Oparia LeTourneau International Airport",
        "OPA",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def chb(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Chan Bay Municipal Airport",
        "CHB",
        re.compile(
            r"\|Gate (?P<code>.*?)\n\|.\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def cbz(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Chan Bay Zeta Airport",
        "CBZ",
        re.compile(r"\|(?P<code>[AB]\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def cbi(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Chan Bay International Airport",
        "CBI",
        re.compile(r"\|(?P<code>\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def dje(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Deadbush Johnston-Euphorial Airport",
        "DJE",
        re.compile(r"\|(?P<code>\d+?)\n\| (?:(?P<airline>[^\n<]*)|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def vda(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Deadbush Valletta Desert Airport",
        "VDA",
        re.compile(r"\|(?P<code>\d+?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def wmi(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "West Mesa International Airport",
        "WMI",
        re.compile(r"\|Gate (?P<code>.*?)\n\| (?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def dfm(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Deadbush Foxfoe Memorial Airport",
        "DFM",
        re.compile(
            r"\|Gate (?P<code>.*?)\n\|(?P<size>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)\n|[^|]*?)"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def dbi(ctx: WikiAirport, cache_dir, timeout):
    html = get_wiki_html("Deadbush International Airport", cache_dir, timeout)
    airport = ctx.extract_get_airport("DBI", "Deadbush International Airport")
    for table in html("table"):
        if (caption := table.caption.string.strip() if table.caption is not None else None) is None:
            continue
        if (
            concourse := "A"
            if "Main" in caption
            else caption[0]
            if caption.endswith("Gates") and caption[0] != "H"
            else None
        ) is None:
            continue
        for tr in table("tr")[1:]:
            code = concourse + tr("td")[0].string
            size = tr("td")[1].string
            airline = tr("td")[2]
            airline = airline.a.string if airline.a is not None else airline.string
            ctx.extract_get_gate(airport, code, size, airline)


@_EXTRACTORS.append
def gsm(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Gemstride Melodia Airfield",
        "GSM",
        re.compile(
            r"\|(?P<code>.*?)\n\|'''(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>[^N]\S[^|]*)|[^|]*?)'''"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def vfw(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Venceslo-Fifth Ward International Airport",
        "VFW",
        re.compile(
            r"\|-\n\|(?P<code>\w*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*|(?P<airline2>\S[^|]*)|[^|]*?)\n\|"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def sdz(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "San Dzobiak International Airport",
        "SDZ",
        re.compile(
            r"\|-\n\|'''(?P<code>\w*?)'''\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*|(?P<airline2>(?!vacant)\S[^|]*)|[^|]*?)\n\|",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def cia(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Carnoustie International Airport",
        "CIA",
        re.compile(
            r"\|\s*(?P<code>.*?)\s*\|\|\s*(?:\[\[(?P<airline>[^|]*?)]]|(?P<airline2>[^|]*?))\s*\|\|",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def erz(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Erzgard International Airport",
        "ERZ",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?P<size>.).*?\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def erz2(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Erzville Passenger Seaport",
        "ERZ",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def atc(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Achowalogen Takachsin-Covina International Airport",
        "ATC",
        re.compile(
            r"\|-\n\|\s*(?P<code>[^|]*?)\s*\|\|[^|]*?\|\|\s*(?:\[\[(?P<airline>[^|]*?)(?:\|[^]]*?|)]][^|]*?|(?P<airline2>[^-|]*?)|-*?)\s*\|\|",
        ),
        cache_dir,
        timeout,
    )
