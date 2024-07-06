from __future__ import annotations

import re
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.wiki_base import get_wiki_html

if TYPE_CHECKING:
    from collections.abc import Callable

    from gatelogue_aggregator.sources.air.wiki_airport import WikiAirport
    from gatelogue_aggregator.types.config import Config

_EXTRACTORS: list[Callable[[WikiAirport, Config], None]] = []


@_EXTRACTORS.append
def pce(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Peacopolis International Airport",
        "PCE",
        re.compile(
            r"(?s)\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*?|)\|\|(?:(?!Service).)*Service"
        ),
        config,
    )


@_EXTRACTORS.append
def mwt(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Miu Wan Tseng Tsz Leng International Airport",
        "MWT",
        re.compile(r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|\n)"),
        config,
    )


@_EXTRACTORS.append
def kek(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Kazeshima Eumi Konaejima Airport",
        "KEK",
        re.compile(r"\|(?P<code>[^|}]*?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)\|\|"),
        config,
    )


@_EXTRACTORS.append
def lar(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Larkspur Lilyflower International Airport",
        "LAR",
        re.compile(r"(?s)'''(?P<code>[^|]*?)'''\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^\n]*?)]]|[^|]*?)\|\|.*?status"),
        config,
    )


@_EXTRACTORS.append
def abg(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Antioch-Bay Point Garvey International Airport",
        "ABG",
        re.compile(
            r"\|(?P<code>.*?\d)\|\| ?(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)(?:\|\||\n)",
        ),
        config,
    )


@_EXTRACTORS.append
def opa(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Oparia LeTourneau International Airport",
        "OPA",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
        ),
        config,
    )


@_EXTRACTORS.append
def chb(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Chan Bay Municipal Airport",
        "CHB",
        re.compile(
            r"\|Gate (?P<code>.*?)\n\|.\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
        ),
        config,
    )


@_EXTRACTORS.append
def cbz(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Chan Bay Zeta Airport",
        "CBZ",
        re.compile(r"\|(?P<code>[AB]\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        config,
    )


@_EXTRACTORS.append
def cbi(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Chan Bay International Airport",
        "CBI",
        re.compile(r"\|(?P<code>\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        config,
    )


@_EXTRACTORS.append
def dje(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Deadbush Johnston-Euphorial Airport",
        "DJE",
        re.compile(r"\|(?P<code>\d+?)\n\| (?:(?P<airline>[^\n<]*)|[^|]*?)"),
        config,
    )


@_EXTRACTORS.append
def vda(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Deadbush Valletta Desert Airport",
        "VDA",
        re.compile(r"\|(?P<code>\d+?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"),
        config,
    )


@_EXTRACTORS.append
def wmi(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "West Mesa International Airport",
        "WMI",
        re.compile(r"\|Gate (?P<code>.*?)\n\| (?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        config,
    )


@_EXTRACTORS.append
def dfm(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Deadbush Foxfoe Memorial Airport",
        "DFM",
        re.compile(
            r"\|Gate (?P<code>.*?)\n\|(?P<size>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)\n|[^|]*?)"
        ),
        config,
    )


@_EXTRACTORS.append
def dbi(ctx: WikiAirport, config):
    html = get_wiki_html("Deadbush International Airport", config)
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
def gsm(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Gemstride Melodia Airfield",
        "GSM",
        re.compile(
            r"\|(?P<code>.*?)\n\|'''(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>[^N]\S[^|]*)|[^|]*?)'''"
        ),
        config,
    )


@_EXTRACTORS.append
def vfw(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Venceslo-Fifth Ward International Airport",
        "VFW",
        re.compile(
            r"\|-\n\|(?P<code>\w*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*|(?P<airline2>\S[^|]*)|[^|]*?)\n\|"
        ),
        config,
    )


@_EXTRACTORS.append
def sdz(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "San Dzobiak International Airport",
        "SDZ",
        re.compile(
            r"\|-\n\|'''(?P<code>\w*?)'''\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*|(?P<airline2>(?!vacant)\S[^|]*)|[^|]*?)\n\|",
        ),
        config,
    )


@_EXTRACTORS.append
def cia(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Carnoustie International Airport",
        "CIA",
        re.compile(
            r"\|\s*(?P<code>.*?)\s*\|\|\s*(?:\[\[(?P<airline>[^|]*?)]]|(?P<airline2>[^|]*?))\s*\|\|",
        ),
        config,
    )


@_EXTRACTORS.append
def erz(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Erzgard International Airport",
        "ERZ",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?P<size>.).*?\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
        ),
        config,
    )


@_EXTRACTORS.append
def erz2(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Erzville Passenger Seaport",
        "ERZ",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
        ),
        config,
    )


@_EXTRACTORS.append
def atc(ctx: WikiAirport, config):
    ctx.regex_extract_airport(
        "Achowalogen Takachsin-Covina International Airport",
        "ATC",
        re.compile(
            r"\|-\n\|\s*(?P<code>[^|]*?)\s*\|\|[^|]*?\|\|\s*(?:\[\[(?P<airline>[^|]*?)(?:\|[^]]*?|)]][^|]*?|(?P<airline2>[^-|]*?)|-*?)\s*\|\|",
        ),
        config,
    )
