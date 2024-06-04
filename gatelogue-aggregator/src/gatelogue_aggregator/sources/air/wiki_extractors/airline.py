from __future__ import annotations

import re
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.air.hardcode import DUPLICATE_GATE_NUM
from gatelogue_aggregator.sources.wiki_base import get_wiki_html

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from gatelogue_aggregator.sources.air.wiki_airline import WikiAirline

_EXTRACTORS: list[Callable[[WikiAirline, Path, int], None]] = []


@_EXTRACTORS.append
def astrella(ctx: WikiAirline, cache_dir, timeout):
    ctx.regex_extract_airline(
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
    ctx.regex_extract_airline(
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
    ctx.regex_extract_airline(
        "BluAir",
        "List of BluAir flights",
        re.compile(
            r"\{\{BA\|BU(?P<code>[^|]*?)\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|[^|]*?\|.}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def intra_air(ctx: WikiAirline, cache_dir, timeout):
    html = get_wiki_html("IntraAir/Flight List", cache_dir, timeout)
    airline = ctx.extract_get_airline("IntraAir", "IntraAir/Flight List")
    for table in html("table"):
        for tr in table("tr")[1::4]:
            if tr("td")[6].find("a", href="/index.php/File:Rsz_open.png") is None:
                continue
            code = tr("td")[1].span.string.removeprefix("Flight ")
            a1 = tr("td")[2].b.string
            a2 = tr("td")[3].b.string
            tr2 = tr.next_sibling.next_sibling

            g1 = tr2("td")[0]("b")
            g1 = f"T{g1[0].string}-{g1[1].string}" if a1 in DUPLICATE_GATE_NUM and len(g1) != 1 else g1[-1].string

            g2 = tr2("td")[1]("b")
            g2 = f"T{g2[0].string}-{g2[1].string}" if a2 in DUPLICATE_GATE_NUM and len(g2) != 1 else g2[-1].string

            g1 = None if g1 == "?" else g1
            g2 = None if g2 == "?" else g2
            ctx.extract_get_flight(airline, code, a1, a2, g1, g2)


@_EXTRACTORS.append
def fli_high(ctx: WikiAirline, cache_dir, timeout):
    html = get_wiki_html("FliHigh Airlines", cache_dir, timeout)
    airline = ctx.extract_get_airline("FliHigh Airlines", "FliHigh Airlines")
    for table in html("table"):
        if table.find(string="Flight #") is None:
            continue
        for tr in table("tr")[1:]:
            if tr("td")[7].find("a", href="/index.php/File:Open.png") is None:
                continue
            code = tr("td")[0].find("span").string.removeprefix("FH")
            a1 = tr("td")[1].b.string
            a2 = tr("td")[2].b.string
            g1 = tr("td")[5].b.string
            g2 = tr("td")[6].b.string
            if "idk" in g1 or "CHECK WIKI" in g1:
                g1 = None
            if "idk" in g2 or "CHECK WIKI" in g2:
                g2 = None
            ctx.extract_get_flight(airline, code, a1, a2, g1, g2)


@_EXTRACTORS.append
def air_mesa(ctx: WikiAirline, cache_dir, timeout):
    ctx.regex_extract_airline(
        "AirMesa",
        "AirMesa",
        re.compile(
            r"\{\{BA\|AM(?P<code>[^|]*?)\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|[^|]*?\|..}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def air(ctx: WikiAirline, cache_dir, timeout):
    ctx.regex_extract_airline(
        "air",
        "Template:Air",
        re.compile(
            r"\{\{BA\|↑↑(?P<code>[^|]*?)\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|[^|]*?\|..}}"
        ),
        cache_dir,
        timeout,
    )
