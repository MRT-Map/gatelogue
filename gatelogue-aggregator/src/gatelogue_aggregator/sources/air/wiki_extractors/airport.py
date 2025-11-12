from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pandas as pd

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.sources.wiki_base import get_wiki_html

if TYPE_CHECKING:
    from collections.abc import Callable

    from gatelogue_aggregator.sources.air.wiki_airport import WikiAirport
    from gatelogue_aggregator.types.config import Config

_EXTRACTORS: list[Callable[[WikiAirport, Config], None]] = []


@_EXTRACTORS.append
def pce(src: WikiAirport, config):
    src.regex_extract_airport(
        "Peacopolis International Airport",
        "PCE",
        re.compile(
            r"(?s)\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*?|)\|\|(?:(?!Service).)*Service"
        ),
        config,
    )


@_EXTRACTORS.append
def mwt(src: WikiAirport, config):
    src.regex_extract_airport(
        "Miu Wan Tseng Tsz Leng International Airport",
        "MWT",
        re.compile(r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|\n)"),
        config,
        size=lambda matches: "XS"
        if (code := matches["code"].removesuffix("A")).startswith("P")
        else "S"
        if int(code) <= 60
        else "M"
        if int(code) <= 82
        else "H",
    )


@_EXTRACTORS.append
def kek(src: WikiAirport, config):
    src.regex_extract_airport(
        "Kazeshima Eumi Konaejima Airport",
        "KEK",
        re.compile(r"\|(?P<code>[^|}]*?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)\|\|"),
        config,
        size=lambda matches: "XS" if int(matches["code"]) > 100 else "SP",
    )


@_EXTRACTORS.append
def abg(src: WikiAirport, config):
    src.regex_extract_airport(
        "Antioch-Bay Point Garvey International Airport",
        "ABG",
        re.compile(
            r"\|(?P<code>.*?\d)\|\| ?(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)(?:\|\||\n)",
        ),
        config,
    )


@_EXTRACTORS.append
def opa(src: WikiAirport, config):
    src.regex_extract_airport(
        "Oparia LeTourneau International Airport",
        "OPA",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
        ),
        config,
    )


@_EXTRACTORS.append
def chb(src: WikiAirport, config):
    src.regex_extract_airport(
        "Chan Bay Municipal Airport",
        "CHB",
        re.compile(
            r"\|Gate (?P<code>.*?)\n\|.\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
        ),
        config,
    )


@_EXTRACTORS.append
def cbz(src: WikiAirport, config):
    src.regex_extract_airport(
        "Chan Bay Zeta Airport",
        "CBZ",
        re.compile(r"\|(?P<code>[AB]\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        config,
        size="S",
    )


@_EXTRACTORS.append
def cbi(src: WikiAirport, config):
    src.regex_extract_airport(
        "Chan Bay International Airport",
        "CBI",
        re.compile(r"\|(?P<code>\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        config,
    )


@_EXTRACTORS.append
def dje(src: WikiAirport, config):
    airport_code = "DJE"
    html = get_wiki_html("Deadbush Johnston-Euphorial Airport", config)
    airport = src.extract_get_airport(airport_code, "Deadbush Johnston-Euphorial Airport")

    for table in html("table"):
        if (caption := table.caption.string.strip() if table.caption is not None else None) is None:
            continue
        if caption == "Terminal 1":
            for tr in table("tr")[1:]:
                code = tr("td")[0].string
                size = "MS" if 1 <= int(code) <= 10 else "S"
                airline = tr("td")[1]
                airline = airline.a.string if airline.a is not None else airline.string
                airline = airline if airline is not None and airline.strip() != "" else None
                src.extract_get_gate(airport, code=code, size=size, airline=airline)
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
                airline = airline if airline is not None and airline.strip() != "" else None
                src.extract_get_gate(airport, code=code, size=size, airline=airline)


@_EXTRACTORS.append
def vda(src: WikiAirport, config):
    src.regex_extract_airport(
        "Deadbush Valletta Desert Airport",
        "VDA",
        re.compile(r"\|(?P<code>\d+?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"),
        config,
        size="S",
    )


@_EXTRACTORS.append
def wmi(src: WikiAirport, config):
    src.regex_extract_airport(
        "West Mesa International Airport",
        "WMI",
        re.compile(r"\|Gate (?P<code>.*?)\n\| (?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)"),
        config,
    )


@_EXTRACTORS.append
def dfm(src: WikiAirport, config):
    src.regex_extract_airport(
        "Deadbush Foxfoe Memorial Airport",
        "DFM",
        re.compile(
            r"\|Gate (?P<code>.*?)\n\|(?P<size>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)\n|[^|]*?)"
        ),
        config,
    )


@_EXTRACTORS.append
def dbi(src: WikiAirport, config):
    html = get_wiki_html("Deadbush International Airport", config)
    airport_code = "DBI"
    airport = src.extract_get_airport(airport_code, "Deadbush International Airport")

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
            src.extract_get_gate(airport, code=code, size=size, airline=airline)


@_EXTRACTORS.append
def gsm(src: WikiAirport, config):
    src.regex_extract_airport(
        "Gemstride Melodia Airfield",
        "GSM",
        re.compile(
            r"\|(?P<code>.*?)\n\|'''(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>[^N]\S[^|]*)|[^|]*?)'''"
        ),
        config,
        size=lambda matches: "H" if matches["code"].startswith("H") else "S",
    )


@_EXTRACTORS.append
def vfw(src: WikiAirport, config):
    src.regex_extract_airport(
        "Venceslo-Fifth Ward International Airport",
        "VFW",
        re.compile(
            r"\|-\n\|(?P<code>\w*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*|(?P<airline2>\S[^|]*)|[^|]*?)\n\|"
        ),
        config,
    )


@_EXTRACTORS.append
def sdz(src: WikiAirport, config):
    src.regex_extract_airport(
        "San Dzobiak International Airport",
        "SDZ",
        re.compile(
            r"\|-\n\|'''(?P<code>\w*?)'''\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*|(?P<airline2>(?!vacant)\S[^|]*)|[^|]*?)\n\|",
        ),
        config,
        size="S",
    )


@_EXTRACTORS.append
def cia(src: WikiAirport, config):
    src.regex_extract_airport(
        "Carnoustie International Airport",
        "CIA",
        re.compile(
            r"\|\s*(?P<code>.*?)\s*\|\|\s*(?:\[\[(?P<airline>[^|]*?)]]|(?P<airline2>[^|]*?))\s*\|\|",
        ),
        config,
    )


@_EXTRACTORS.append
def erz(src: WikiAirport, config):
    src.regex_extract_airport(
        "Erzgard International Airport",
        "ERZ",
        re.compile(
            r"\|-\n\|(?P<code>.*?)\n\|(?P<size>.).*?\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
        ),
        config,
    )


@_EXTRACTORS.append
def erz2(src: WikiAirport, config):
    src.regex_extract_airport(
        "Erzville Passenger Seaport",
        "ERZ",
        re.compile(
            r"\|-\n\|(?P<code>S.*?)\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
        ),
        config,
        size="SP",
    )


@_EXTRACTORS.append
def atc(src: WikiAirport, config):
    src.regex_extract_airport(
        "Achowalogen Takachsin-Covina International Airport",
        "ATC",
        re.compile(
            r"\|-\n\|\s*(?P<code>[^|]*?)\s*\|\|[^|]*?\|\|\s*(?:\[\[(?P<airline>[^|]*?)(?:\|[^]]*?|)]][^|]*?|(?P<airline2>[^-|]*?)|-*?)\s*\|\|",
        ),
        config,
    )


@_EXTRACTORS.append
def aix(src: WikiAirport, config):
    cache = config.cache_dir / "aix"
    airport_code = "AIX"
    airport = src.extract_get_airport(airport_code, "Aurora International Airport")

    get_url(
        "https://docs.google.com/spreadsheets/d/1vG_oEj_XzZlckRwxn4jKkK1FcgjjaULpt66XcxClqP8/export?format=csv&gid=0",
        cache,
        timeout=config.timeout,
        cooldown=config.cooldown,
    )

    df = pd.read_csv(cache, header=1)

    d = list(zip(df["Gate ID"], df["Gate Size"], df["Company"], strict=False))

    old_gate_size = None
    for gate_code, gate_size, airline in d:
        if str(gate_size) == "nan":
            gate_size = old_gate_size  # noqa: PLW2901
        else:
            gate_size = str(gate_size)[0]  # noqa: PLW2901
            old_gate_size = gate_size
        src.extract_get_gate(
            airport=airport,
            code=gate_code,
            airline=airline if str(airline) != "nan" and airline != "Unavailable" else None,
            size=gate_size,
        )


@_EXTRACTORS.append
def lar(src: WikiAirport, config):
    cache = config.cache_dir / "lar"
    airport_code = "LAR"
    airport = src.extract_get_airport(airport_code, "Larkspur Lilyflower International Airport")

    get_url(
        "https://docs.google.com/spreadsheets/d/1TjGME8Hx_Fh5F0zgHBBvAj_Axlyk4bztUBELiEu4m-w/export?format=csv&gid=0",
        cache,
        timeout=config.timeout,
        cooldown=config.cooldown,
    )

    df = pd.read_csv(cache)

    d = list(zip(df["Gate"], df["Size"], df["Airline"], df["Status"], strict=False))

    for gate_code, size, airline, _status in d:
        src.extract_get_gate(
            airport=airport,
            code=gate_code,
            size=size,
            airline=airline if str(airline) != "nan" and airline != "?" else None,
        )


@_EXTRACTORS.append
def lfa(src: WikiAirport, config):
    cache = config.cache_dir / "lfa"
    airport_code = "LFA"
    airport = src.extract_get_airport(airport_code, "Larkspur Lilyflower International Airport")

    get_url(
        "https://docs.google.com/spreadsheets/d/1TjGME8Hx_Fh5F0zgHBBvAj_Axlyk4bztUBELiEu4m-w/export?format=csv&gid=1289412824",
        cache,
        timeout=config.timeout,
        cooldown=config.cooldown,
    )

    df = pd.read_csv(cache)

    d = list(zip(df["Gate"], df["Size"], df["Airline"], df["Status"], strict=False))

    for gate_code, size, airline, _status in d:
        src.extract_get_gate(
            airport=airport,
            code=gate_code,
            size=size,
            airline=airline if str(airline) != "nan" and airline != "?" else None,
        )
