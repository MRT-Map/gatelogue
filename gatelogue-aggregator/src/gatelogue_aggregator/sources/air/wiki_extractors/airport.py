from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pandas as pd
import rich

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.logging import ERROR, RESULT
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
    html = get_wiki_html("Deadbush Johnston-Euphorial Airport", config)
    airport = ctx.extract_get_airport("DJE", "Deadbush Johnston-Euphorial Airportt")
    for table in html("table"):
        if (caption := table.caption.string.strip() if table.caption is not None else None) is None:
            continue
        if caption == "Terminal 1":
            for tr in table("tr")[1:]:
                code = tr("td")[0].string
                size = "MS" if 1 <= int(code) <= 10 else "S"  # noqa: PLR2004
                airline = tr("td")[1]
                airline = airline.a.string if airline.a is not None else airline.string
                ctx.extract_get_gate(airport, code=code, size=size, airline=airline)
        elif caption == "Terminal 2":
            concourse = ""
            for tr in table("tr")[1:]:
                if len(tr("td")) == 1:
                    concourse = tr.find("b").string.strip(" ")[0]
                    continue
                code = concourse + tr("td")[0].string
                size = "S"
                airline = tr("td")[1]
                airline = airline.a.string if airline.a is not None else airline.string
                ctx.extract_get_gate(airport, code=code, size=size, airline=airline)


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
            ctx.extract_get_gate(airport, code=code, size=size, airline=airline)


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


@_EXTRACTORS.append
def aix(ctx: WikiAirport, config):
    cache = config.cache_dir / "aix"
    airport_code = "AIX"
    airport = ctx.extract_get_airport(airport_code, "Aurora International Airport")

    get_url(
        "https://docs.google.com/spreadsheets/d/1vG_oEj_XzZlckRwxn4jKkK1FcgjjaULpt66XcxClqP8/export?format=csv&gid=0",
        cache,
        timeout=config.timeout,
    )

    df = pd.read_csv(cache, header=1)

    d = list(zip(df["Gate ID"], df["Company"], strict=False))

    result = 0
    for gate_code, airline in d:
        ctx.extract_get_gate(
            airport=airport,
            code=gate_code,
            airline=airline if str(airline) != "nan" or airline != "Unavailable" else None,
        )
        result += 1

    if not result:
        rich.print(ERROR + f"Extraction for {airport_code} yielded no results")
    else:
        rich.print(RESULT + f"{airport_code} has {result} gates")


@_EXTRACTORS.append
def lar(ctx: WikiAirport, config):
    cache = config.cache_dir / "lar"
    airport_code = "LAR"
    airport = ctx.extract_get_airport(airport_code, "Larkspur Lilyflower International Airport")

    get_url(
        "https://docs.google.com/spreadsheets/d/1TjGME8Hx_Fh5F0zgHBBvAj_Axlyk4bztUBELiEu4m-w/export?format=csv&gid=0",
        cache,
        timeout=config.timeout,
    )

    df = pd.read_csv(cache)

    d = list(zip(df["Gate"], df["Size"], df["Airline"], df["Status"], strict=False))

    result = 0
    for gate_code, size, airline, status in d:
        ctx.extract_get_gate(
            airport=airport,
            code=gate_code,
            size=size,
            airline=airline if str(airline) != "nan" or airline != "?" else None,
        )
        result += 1

    if not result:
        rich.print(ERROR + f"Extraction for {airport_code} yielded no results")
    else:
        rich.print(RESULT + f"{airport_code} has {result} gates")


@_EXTRACTORS.append
def lfa(ctx: WikiAirport, config):
    cache = config.cache_dir / "lfa"
    airport_code = "LFA"
    airport = ctx.extract_get_airport(airport_code, "Larkspur Lilyflower International Airport")

    get_url(
        "https://docs.google.com/spreadsheets/d/1TjGME8Hx_Fh5F0zgHBBvAj_Axlyk4bztUBELiEu4m-w/export?format=csv&gid=1289412824",
        cache,
        timeout=config.timeout,
    )

    df = pd.read_csv(cache)

    d = list(zip(df["Gate"], df["Size"], df["Airline"], df["Status"], strict=False))

    result = 0
    for gate_code, size, airline, status in d:
        ctx.extract_get_gate(
            airport=airport,
            code=gate_code,
            size=size,
            airline=airline if str(airline) != "nan" or airline != "?" else None,
        )
        result += 1

    if not result:
        rich.print(ERROR + f"Extraction for {airport_code} yielded no results")
    else:
        rich.print(RESULT + f"{airport_code} has {result} gates")
