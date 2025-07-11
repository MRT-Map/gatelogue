from __future__ import annotations

import itertools
import re
from typing import TYPE_CHECKING

import pandas as pd

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.sources.air.hardcode import DUPLICATE_GATE_NUM
from gatelogue_aggregator.sources.wiki_base import get_wiki_html

if TYPE_CHECKING:
    from collections.abc import Callable

    from gatelogue_aggregator.sources.air.wiki_airline import WikiAirline
    from gatelogue_aggregator.types.config import Config

_EXTRACTORS: list[Callable[[WikiAirline, Config], None]] = []


@_EXTRACTORS.append
def astrella(src: WikiAirline, config):
    src.regex_extract_airline(
        "Astrella",
        "Astrella",
        re.compile(
            r"\{\{AstrellaFlight\|code = AA(?P<code>[^$\n]*?)\|airport1 = (?P<a1>[^\n]*?)\|gate1 = (?P<g1>[^\n]*?)\|airport2 = (?P<a2>[^\n]*?)\|gate2 = (?P<g2>[^\n]*?)\|size = (?P<s>[^\n]*?)\|status = active}}"
        ),
        config,
    )


@_EXTRACTORS.append
def turbula(src: WikiAirline, config):
    src.regex_extract_airline(
        "Turbula",
        "Template:TurbulaFlightList",
        re.compile(
            r"\{\{AstrellaFlight\|imgname = Turbula\|code = LU(?P<code>[^$\n]*?)\|airport1 = (?P<a1>[^\n]*?)(?:\|gate1 = (?P<g1>[^\n]*?)|)\|airport2 = (?P<a2>[^\n]*?)(?:\|gate2 = (?P<g2>[^\n]*?)|)\|[^|]*?\|status = active}}"
        ),
        config,
        size="SP",
    )


@_EXTRACTORS.append
def blu_air(src: WikiAirline, config):
    src.regex_extract_airline(
        "BluAir",
        "List of BluAir flights",
        re.compile(
            r"\{\{BA\|BU(?P<code>[^|<]*)[^|]*?\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|[^|]*?\|.}}"
        ),
        config,
    )


@_EXTRACTORS.append
def intra_air(src: WikiAirline, config):
    html = get_wiki_html("IntraAir/Flight List", config)
    airline_name = "IntraAir"
    airline = src.extract_get_airline(airline_name, "IntraAir/Flight List")

    for table in html("table"):
        for tr in table("tr")[1::4]:
            if len(tr("td")) < 7:  # noqa: PLR2004
                continue
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
            s = "H" if 1400 <= int(code) <= 1799 else "SP" if 1800 <= int(code) >= 2000 else None  # noqa: PLR2004
            src.extract_get_flight(airline, code=code, a1=a1, a2=a2, g1=g1, g2=g2, s=s)


@_EXTRACTORS.append
def fli_high(src: WikiAirline, config):
    html = get_wiki_html("FliHigh Airlines", config)
    airline_name = "FliHigh Airlines"
    airline = src.extract_get_airline(airline_name, airline_name)

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
            src.extract_get_flight(airline, code=code, a1=a1, a2=a2, g1=g1, g2=g2)


@_EXTRACTORS.append
def air_mesa(src: WikiAirline, config):
    src.regex_extract_airline(
        "AirMesa",
        "AirMesa",
        re.compile(
            r"\{\{BA\|AM(?P<code>[^|]*?)\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|[^|]*?\|..}}"
        ),
        config,
    )


@_EXTRACTORS.append
def air(src: WikiAirline, config):
    src.regex_extract_airline(
        "air",
        "Template:Air",
        re.compile(
            r"\{\{BA\|↑↑(?P<code>[^|]*?)\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|[^|]*?\|..}}"
        ),
        config,
    )


@_EXTRACTORS.append
def berryessa(src: WikiAirline, config):
    src.regex_extract_airline(
        "Berryessa Airlines",
        "Berryessa Airlines",
        re.compile(
            r"\{\{BA\|IN(?P<code>[^|<]*)[^|]*?\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|[^|]*?\|..}}"
        ),
        config,
    )


@_EXTRACTORS.append
def air_net(src: WikiAirline, config):
    html = get_wiki_html("AirNet", config)
    airline_name = "AirNet"
    airline = src.extract_get_airline(airline_name, airline_name)

    table = next(a for a in html("table") if "Number" in str(a))
    for tr in table.tbody("tr")[1:]:
        if "Boarding" not in str(tr("td")[3]):
            continue
        code = next(tr("td")[0].strings).removeprefix("AN")
        ng1 = "".join(tr("td")[1].strings)
        ng2 = "".join(tr("td")[2].strings)
        n1, g1 = ng1.split("|")
        n2, g2 = ng2.split("|")

        src.extract_get_flight(airline, code=code, n1=n1, n2=n2, g1=g1, g2=g2)


@_EXTRACTORS.append
def fly_creeper(src: WikiAirline, config):
    html = get_wiki_html("FlyCreeper", config)
    airline_name = "FlyCreeper"
    airline = src.extract_get_airline(airline_name, airline_name)

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
            g1 = next(iter(tr("td")[4].strings))
            g2 = list(tr("td")[4].strings)[1]
            src.extract_get_flight(
                airline, code=code, a1=a1, a2=a2, g1=g1, g2=g2, s="H" if code.endswith("H") else None
            )


@_EXTRACTORS.append
def continental(src: WikiAirline, config):
    src.regex_extract_airline(
        "Continental Airlines",
        "Continental Airlines",
        re.compile(
            r"\|-\n\|.*?\n\|(?:CO)?(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|(?P<g1>[^|]*?)\n\|(?P<g2>[^|]*?)\n\|{{status\|good}}",
            re.IGNORECASE,
        ),
        config,
    )


@_EXTRACTORS.append
def air_kanata(src: WikiAirline, config):
    src.regex_extract_airline(
        "Air Kanata",
        "Air Kanata",
        re.compile(
            r"\|-\n\|AK(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}"
        ),
        config,
    )


@_EXTRACTORS.append
def jiffy_air(src: WikiAirline, config):
    src.regex_extract_airline(
        "JiffyAir",
        "JiffyAir",
        re.compile(
            r"\|-\n\|JF(?P<code>[^|]*?)\n\|(?:{{afn\|(?P<a1>[^|]*?)}}|.*?\((?P<a12>[^|]*?)\))\n\|(?:{{afn\|(?P<a2>[^|]*?)}}|.*?\((?P<a22>[^|]*?)\))\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}"
        ),
        config,
    )


# @_EXTRACTORS.append
# def jiffy_air2(src: WikiAirline, config):
#     src.regex_extract_airline(
#         "JiffyAir",
#         "JiffyAir",
#         re.compile(
#             r"""\|-
# \|rowspan=\"2\"\|JF(?P<code>[^|]*?)
# \|(?:{{afn\|(?P<a1>[^|]*?)}}|.*?\((?P<a12>[^|]*?)\))
# \|(?:{{afn\|(?P<a2>[^|]*?)}}|.*?\((?P<a22>[^|]*?)\))
# \|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''
# \|rowspan=\"2\"\|{{[sS]tatus\|good}}
# \|rowspan=\"2\"\|[^\n]*?
# \|-
# \|[^\n]*?
# \|(?:{{afn\|(?P<a3>[^|]*?)}}|.*?\((?P<a32>[^|]*?)\))
# \|'''[^|]*?'''\n\|'''(?P<g3>[^|]*?)'''"""
#         ),
#         config,
#     )


@_EXTRACTORS.append
def tennoji(src: WikiAirline, config):
    src.regex_extract_airline(
        "Tennoji Airways",
        "Tennoji Airways",
        re.compile(
            r"\|-\n\|(?:TA|RK)(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}"
        ),
        config,
        size=lambda matches: "H" if matches["code"].startswith("H") else None,
    )


@_EXTRACTORS.append
def yousoro(src: WikiAirline, config):
    src.regex_extract_airline(
        "Yousoro!",
        "Yousoro!",
        re.compile(
            r"\|-\n\|RKS(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}"
        ),
        config,
        size="SP",
    )


@_EXTRACTORS.append
def rainer_airways(src: WikiAirline, config):
    src.regex_extract_airline(
        "Rainer Airways",
        "Rainer Airways",
        re.compile(
            r"""\|-
\|RB(?P<code>.*?)
\|(?:{{afn\|(?P<a1>.*?)}}|.*?\((?P<a12>.*?)\))
\|(?P<g1>.*?)
\|(?:{{afn\|(?P<a2>.*?)}}|.*?\((?P<a22>.*?)\))
\|(?P<g2>.*?)
"""
        ),
        config,
    )


@_EXTRACTORS.append
def marble(src: WikiAirline, config):
    src.regex_extract_airline(
        "MarbleAir",
        "MarbleAir",
        re.compile(r"\|-\n\|'''MA(?P<code>.*?)'''\n.*?\n\|.*?\((?P<a1>.*?)\)\n\|.*?\((?P<a2>.*?)\)\n\|.*?\n\|Active"),
        config,
    )


@_EXTRACTORS.append
def amber_air(src: WikiAirline, config):
    src.regex_extract_airline(
        "AmberAir",
        "AmberAir",
        re.compile(r"""\|-
\|'''AB(?P<code>.*?)/.*?'''
\|'''(?:\[\[.*?\|(?P<a1>[^|]*?)]]|(?P<a12>[^|']*))'''.*?
'''to (?:\[\[.*?\|(?P<a2>[^|]*?)]]|(?P<a22>[^|']*))'''.*?
\|(?:'''(?P<g1>[^|]*?)'''|)
\|(?:'''(?P<g2>[^|].*?)'''|)
\|.*?
\|\[\[File:Service Good\.png\|50px]]"""),
        config,
    )


@_EXTRACTORS.append
def arctic_air(src: WikiAirline, config):
    cache = config.cache_dir / "arctic_air"
    airline_name = "ArcticAir"
    airline = src.extract_get_airline(airline_name, airline_name)

    get_url(
        "https://docs.google.com/spreadsheets/d/1XhIW2kdX_d56qpT-kyGz6tD9ZuPQtqSeFZvPiqMDAVU/export?format=csv&gid=0",
        cache,
        timeout=config.timeout,
        cooldown=config.cooldown,
    )

    df = pd.read_csv(cache)

    d = list(zip(df["Flight"], df["Departure"], df["Arrival"], df["D. Gate"], df["A. Gate"], strict=False))

    for flight, a1, a2, g1, g2 in d[::2]:
        if str(flight).strip() in ("227", "228", "239", "240"):
            continue
        if not a1 or str(a1) == "nan":
            continue

        if str(a1).strip() not in DUPLICATE_GATE_NUM:
            g1 = re.sub(r"T. ", "", str(g1))  # noqa: PLW2901
        if str(a2).strip() not in DUPLICATE_GATE_NUM:
            g2 = re.sub(r"T. ", "", str(g2))  # noqa: PLW2901

        src.extract_get_flight(
            airline, code=str(flight), a1=a1, a2=a2, g1=g1 if "*" not in g1 else None, g2=g2 if "*" not in g2 else None
        )


@_EXTRACTORS.append
def sandstone_airr(src: WikiAirline, config):
    cache = config.cache_dir / "sandstone_airr"
    airline_name = "Sandstone Airr"
    airline = src.extract_get_airline(airline_name, airline_name)

    get_url(
        "https://docs.google.com/spreadsheets/d/1XhIW2kdX_d56qpT-kyGz6tD9ZuPQtqSeFZvPiqMDAVU/export?format=csv&gid=3084051",
        cache,
        timeout=config.timeout,
        cooldown=config.cooldown,
    )

    df = pd.read_csv(cache)

    d = list(zip(df["Unnamed: 1"], df["Airport"], df["Gate"], strict=False))

    for (flight, a1, g1), (_, a2, g2) in list(itertools.pairwise(d))[::2]:
        if not a1 or str(a1) == "nan":
            continue

        if str(a1).strip() not in DUPLICATE_GATE_NUM:
            g1 = re.sub(r"T. ", "", str(g1))  # noqa: PLW2901
        if str(a2).strip() not in DUPLICATE_GATE_NUM:
            g2 = re.sub(r"T. ", "", str(g2))  # noqa: PLW2901

        src.extract_get_flight(
            airline,
            code=str(int(flight)),
            a1=a1,
            a2=a2,
            g1=g1 if "*" not in g1 else None,
            g2=g2 if "*" not in g2 else None,
        )


@_EXTRACTORS.append
def michigana(src: WikiAirline, config):
    src.regex_extract_airline(
        "Michigana",
        "Template:Michigana",
        re.compile(r"""\|\|<font size="4">'''MI(?P<code>.*?)'''</font>
\|\|<font size="4">'''(?P<a1>.*?)'''</font> <br/>.*?
\|\|.*?
\|\|<font size="4">'''(?P<a2>.*?)'''</font> <br/>.*?
\|\|.*?
\|\| \[\[File:Eastern Active1\.png\|50px]]"""),
        config,
    )


@_EXTRACTORS.append
def lilyflower_airlines(src: WikiAirline, config):
    cache = config.cache_dir / "lilyflower"
    airline_name = "Lilyflower Airlines"
    airline = src.extract_get_airline(airline_name, airline_name)

    get_url(
        "https://docs.google.com/spreadsheets/d/1B-fSerCAQAtaW-kAfv1npdjpGt-N1PrB1iUOmUBX5HI/export?format=csv&gid=1864111212",
        cache,
        timeout=config.timeout,
        cooldown=config.cooldown,
    )

    df = pd.read_csv(cache, header=1)

    d = list(zip(df["Flight"], df["IATA"], df["Gate"], df["IATA.1"], df["Gate.1"], strict=False))

    for flight, a1, g1, a2, g2 in d:
        if not a1 or str(a1) == "nan":
            continue
        src.extract_get_flight(
            airline,
            code=str(int(flight)),
            a1=a1,
            a2=a2,
            g1=g1,
            g2=g2,
        )


@_EXTRACTORS.append
def rodbla(src: WikiAirline, config):
    src.regex_extract_airline(
        "RodBla Heli",
        "RodBla Heli",
        re.compile(r"\|RB(?P<code>.*?)\n\|Active\n\|(?P<a1>.*?)-(?P<a2>.*?)\n"),
        config,
        size="H",
    )


@_EXTRACTORS.append
def mylesheli(src: WikiAirline, config):
    def _hack(matches):
        if matches["a1"] == "GSA":
            matches["a1"] = "GSAH"
        if matches["a2"] == "GSA":
            matches["a2"] = "GSAH"
        return "H"

    src.regex_extract_airline(
        "MylesHeli",
        "MylesHeli/Flights",
        re.compile(r"{{mylesh\|MY(?P<code>.*?)\|t\|(?P<a1>.*?)\|.*?\|.*?\|(?P<a2>.*?)\|.*?\|.*?}}"),
        config,
        size=_hack,
    )


@_EXTRACTORS.append
def aero(src: WikiAirline, config):
    src.regex_extract_airline(
        "aero",
        "Aero",
        re.compile(r"""\|\|<font size="4">'''ae(?P<code>.*?)'''.*?
\|\|<font size="4">'''(?P<a1>.*?)'''(?:.*?gate (?P<g1>.*?)[)']|).*?
\|\|.*?
\|\|<font size="4">'''(?P<a2>.*?)'''(?:.*?gate (?P<g2>.*?)[)']|).*?
\|\|.*?
\|\|.*?
\|\|.*?\[\[File:Eastern Active\.gif\|50px]]"""),
        config,
    )


@_EXTRACTORS.append
def south_weast(src: WikiAirline, config):
    html = get_wiki_html("South Weast Airlines", config)
    airline_name = "South Weast Airlines"
    airline = src.extract_get_airline(airline_name, airline_name)

    table = next(a for a in html("table") if "Flight Number" in str(a))
    for tr in table.tbody("tr")[1:]:
        if "ON TIME" not in str(tr("td")[4]):
            continue
        code = tr("td")[0].string
        n1 = "".join(tr("td")[2].strings)
        n2 = "".join(tr("td")[3].strings)

        src.extract_get_flight(airline, code=code, n1=n1, n2=n2, s="H" if code.startswith("H") else None)


@_EXTRACTORS.append
def utopiair(src: WikiAirline, config):
    html = get_wiki_html("UtopiAir", config)
    airline_name = "UtopiAir"
    airline = src.extract_get_airline(airline_name, airline_name)

    for table in (a for a in html("table") if "Flight" in str(a)):
        for tr in table.tbody("tr")[1:]:
            if len(tr("td")) > 3 and "ON TIME" not in str(tr("td")[3]):  # noqa: PLR2004
                continue
            code = tr("td")[0].string
            n1 = "".join(tr("td")[1].strings)
            n2 = "".join(tr("td")[2].strings)

            src.extract_get_flight(airline, code=code, n1=n1, n2=n2, s="SP" if int(code) >= 500 else None)  # noqa: PLR2004ranges for direction + fix caelus


@_EXTRACTORS.append
def southeastern_airways(src: WikiAirline, config):
    src.regex_extract_airline(
        "Southeastern Airways",
        "Template:Southeastern Airways Flight List",
        re.compile(r"""\|\|.*?'''SE(?P<code>.*?)'''.*?
\|\|.*?'''(?:\[\[.*?\||\[\[)?(?P<a1>.*?)(?:]])?'''.*?
\|\|.*?
\|\|.*?'''(?:\[\[.*?\||\[\[)?(?P<a2>.*?)(?:]])?'''.*?
\|\|\[\[File:Eastern Active\.gif"""),
        config,
    )


@_EXTRACTORS.append
def caelus1(src: WikiAirline, config):
    for series in ("0", "1", "2", "7"):
        src.regex_extract_airline(
            "Caelus Airlines",
            f"Template:ICAG {series}00 Series Flights",
            re.compile(r"""(?s)\|-
! .*?
! .*?CL (?P<code>.*?)<.*?
! .*?'''(?P<a1>.*?)'''.*?
! .*?'''(?P<a2>.*?)'''.*?
! .*?
! .*?CaelusAirlines_Boarding\.png"""),
            config,
        )


@_EXTRACTORS.append
def caelus2(src: WikiAirline, config):
    html = get_wiki_html("Template:ICAG 300 Series Flights", config)
    airline_name = "Caelus Airlines"
    airline = src.extract_get_airline(airline_name, airline_name)

    table = next(a for a in html("table") if "Operated by" in str(a))
    for tr in table.tbody("tr")[1:]:
        if "CaelusAirlines_Boarding.png" not in str(tr("td")[4]):
            continue
        codes = set(tr("td")[1].string.removeprefix("Flight ").split("/"))
        a1, a2 = (b.string for b in tr("td")[2]("b"))
        src.extract_get_flight(airline, code=codes, a1=a1, a2=a2)


@_EXTRACTORS.append
def caelus_link(src: WikiAirline, config):
    html = get_wiki_html("Template:ICAG 400 Series Flights", config)
    airline_name = "CaelusLink"
    airline = src.extract_get_airline(airline_name, airline_name)

    table = next(a for a in html("table") if "Operated by" in str(a))
    for tr in table.tbody("tr")[1:]:
        if "CaelusAirlines_Boarding.png" not in str(tr("td")[4]):
            continue
        codes = set(tr("td")[1].string.removeprefix("Flight ").split("/"))
        n1, n2 = tr("td")[2].strings
        src.extract_get_flight(airline, code=codes, n1=n1, n2=n2)


@_EXTRACTORS.append
def cbc(src: WikiAirline, config):
    src.regex_extract_airline(
        "Caravacan Biplane Company",
        "Caravacan Biplane Company",
        re.compile(r"""(?P<code>.*?)\. (?P<a1>.*?) --- (?P<a2>.*?) /"""),
        config,
    )


@_EXTRACTORS.append
def cascadia(src: WikiAirline, config):
    src.regex_extract_airline(
        "Cascadia Airways",
        "Template:CascadiaAirGroupCA",
        re.compile(r"""\|- ?
! .*?
\|.*?
\|\|.*?'''CA (?P<code>.*?)'''.*?
\|\|.*?'''(?P<a1>.*?)(?: & (?P<a3>.*?))?'''.*?
\|\|.*?
\|\|.*?'''(?P<a2>.*?)'''.*?
\|\|.*?
\|\| \[\[File:Eastern Active1\.png"""),
        config,
    )


@_EXTRACTORS.append
def waviation1(src: WikiAirline, config):
    html = get_wiki_html("Waviation", config)
    airline_name = "Waviation"
    airline = src.extract_get_airline(airline_name, airline_name)

    for table in html("table"):
        if (caption := table.find("caption")) is None or (
            "(000s)" not in str(caption) and "(1000s)" not in str(caption)
        ):
            continue
        for tr in table.tbody("tr")[1:]:
            if "N/A" not in str(tr("td")[7]):
                continue
            codes = set(tr("td")[0].string.split("/"))
            a1 = tr("td")[1].b.string
            g1 = tr("td")[2].string
            a2 = tr("td")[3].b.string
            g2 = tr("td")[4].string
            if "XX" in g1:
                g1 = None
            if "XX" in g2:
                g2 = None
            src.extract_get_flight(airline, code=codes, a1=a1, a2=a2, g1=g1, g2=g2)


@_EXTRACTORS.append
def waviation2(src: WikiAirline, config):
    html = get_wiki_html("Waviation", config)
    airline_name = "Waviation"
    airline = src.extract_get_airline(airline_name, airline_name)

    for table in html("table"):
        if (caption := table.find("caption")) is None or "(000s)" in str(caption) or "(1000s)" in str(caption):
            continue

        a1 = (
            "AIX"
            if "(300s)" in str(caption)
            else "LNT"
            if "(400s)" in str(caption)
            else "DJE"
            if "(500s)" in str(caption)
            else "NPR"
            if "(600s)" in str(caption)
            else None
        )
        if a1 is None:
            continue

        for tr in table.tbody("tr")[1:]:
            if "N/A" not in str(tr("td")[6]):
                continue
            codes = set(tr("td")[0].string.split("/"))
            g1 = tr("td")[1].string
            a2 = tr("td")[2].b.string
            g2 = tr("td")[3].string
            if "XX" in g1:
                g1 = None
            if "XX" in g2:
                g2 = None
            src.extract_get_flight(airline, code=codes, a1=a1, a2=a2, g1=g1, g2=g2)
