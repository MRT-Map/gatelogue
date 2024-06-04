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


@_EXTRACTORS.append
def infamous(ctx: WikiAirline, cache_dir, timeout):
    ctx.regex_extract_airline(
        "Infamous Airlines",
        "Infamous Airlines",
        re.compile(
            r"\{\{BA\|IN(?P<code>[^|]*?)\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|[^|]*?\|..}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def fly_creeper(ctx: WikiAirline, cache_dir, timeout):
    html = get_wiki_html("FlyCreeper", cache_dir, timeout)
    airline = ctx.extract_get_airline("FlyCreeper", "FlyCreeper")
    for table in html("table"):
        if "Flight No" not in str(table):
            continue
        for tr in table.tbody("tr")[1:]:
            if "Active" not in tr("td")[2].string:
                continue
            code = tr("td")[0].string.removeprefix("FC").strip()
            if (a1 := re.search(r"\((...)\)", str(tr("td")[3]("b")[0]))) is None:
                continue
            a1 = a1.group(1)
            if "?" in a1:
                a1 = None
            if (a2 := re.search(r"\((...)\)", str(tr("td")[3]("b")[1]))) is None:
                continue
            a2 = a2.group(1)
            if "?" in a2:
                a2 = None
            g1 = list(tr("td")[4].strings)[0]
            g2 = list(tr("td")[4].strings)[1]
            ctx.extract_get_flight(airline, code, a1, a2, g1, g2)


@_EXTRACTORS.append
def continental(ctx: WikiAirline, cache_dir, timeout):
    ctx.regex_extract_airline(
        "Continental Airlines",
        "Continental",
        re.compile(
            r"\|-\n\|CO(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|(?P<g1>[^|]*?)\n\|(?P<g2>[^|]*?)\n\|{{status\|good}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def air_kanata(ctx: WikiAirline, cache_dir, timeout):
    ctx.regex_extract_airline(
        "Air Kanata",
        "Air Kanata",
        re.compile(
            r"\|-\n\|AK(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def raiko(ctx: WikiAirline, cache_dir, timeout):
    ctx.regex_extract_airline(
        "Raiko Airlines",
        "Raiko Airlines",
        re.compile(
            r"\|-\n\|RK(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}"
        ),
        cache_dir,
        timeout,
    )


@_EXTRACTORS.append
def rainer_airways(ctx: WikiAirline, cache_dir, timeout):
    # INCOMPLETE
    ctx.regex_extract_airline(
        "Rainer Airways",
        "Rainer Airways",
        re.compile(
            r"\|-\n\|\s*RB(?P<code>[^|]*?)\s*\n\|\s*{{afn\|(?P<a1>.*?)}}\s*\n\|\s*(?P<g1>.*?)\s*\n\|\s*{{afn\|(?P<a2>.*?)}}\s*\n\|\s*(?P<g2>.*?)\s*\n"
        ),
        cache_dir,
        timeout,
    )
