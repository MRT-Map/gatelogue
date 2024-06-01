from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.sources.wiki_airport import WikiAirport

_EXTRACTORS: list[Callable[[WikiAirport, Path, int], None]] = []


@_EXTRACTORS.append
def pce(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Peacopolis International Airport",
        "PCE",
        re.compile(r"\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]].*?|)\|\|.*Service"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def mwt(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Miu Wan Tseng Tsz Leng International Airport",
        "MWT",
        re.compile(r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|\n)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def kek(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Kazeshima Eumi Konaejima Airport",
        "KEK",
        re.compile(r"\|(?P<code>[^|}]*?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)\|\|"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def lar(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Larkspur Lilyflower International Airport",
        "LAR",
        re.compile(r"(?s)'''(?P<code>[^|]*?)'''\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)\|\|.*?status"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def abg(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
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
    ctx.regex_extract_airport(
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
    ctx.regex_extract_airport(
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
    ctx.regex_extract_airport(
        "Chan Bay Zeta Airport",
        "CBZ",
        re.compile(r"\|(?P<code>[AB]\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def cbi(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "Chan Bay International Airport",
        "CBI",
        re.compile(r"\|(?P<code>\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)"),
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
        re.compile(r"\|(?P<code>\d+?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def wmi(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
        "West Mesa International Airport",
        "WMI",
        re.compile(r"\|Gate (?P<code>.*?)\n\| (?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)"),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def dfm(ctx: WikiAirport, cache_dir, timeout):
    ctx.regex_extract_airport(
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
    ctx.regex_extract_airport(
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
    ctx.regex_extract_airport(
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
    ctx.regex_extract_airport(
        "San Dzobiak International Airport",
        "SDZ",
        re.compile(
            r"\|-\n\|(?P<code>\w\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)",
            re.MULTILINE,
        ),
        cache_dir,
        timeout,
    )
