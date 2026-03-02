from __future__ import annotations

import itertools
import re
from typing import TYPE_CHECKING

import pandas as pd

import gatelogue_types as gt
from gatelogue_aggregator.downloader import get_csv, get_wiki_html, get_wiki_link, get_wiki_text
from gatelogue_aggregator.source import AirSource
from gatelogue_aggregator.sources.air.hardcode import DUPLICATE_GATE_NUM
from gatelogue_aggregator.sources.air.wiki_airline import RegexWikiAirline

if TYPE_CHECKING:
    import bs4

    from gatelogue_aggregator.config import Config

AIRLINE_SOURCES: list[type[AirSource]] = []


@AIRLINE_SOURCES.append
class Astrella(RegexWikiAirline):
    airline_name = "Astrella"
    page_name = "Astrella"
    regex = re.compile(
        r"\{\{AstrellaFlight\|code = AA(?P<code>[^$\n]*?)\|airport1 = (?P<a1>[^\n]*?)\|gate1 = (?P<g1>[^\n]*?)\|airport2 = (?P<a2>[^\n]*?)\|gate2 = (?P<g2>[^\n]*?)\|size = (?P<s>[^\n]*?)\|status = active}}"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        match matches["s"]:
            case "XS":
                return "Astrella XS"
            case "S":
                return "Astrella S"
            case "MS":
                return "Astrella MS"
            case "M":
                return "Astrella M"
            case "ML":
                return "Astrella ML"
            case other:
                raise ValueError(other)

    @staticmethod
    def process_flight_code_back(code: str) -> str:
        return str(int(code) + 1)


@AIRLINE_SOURCES.append
class Turbula(RegexWikiAirline):
    airline_name = "Turbula"
    page_name = "Template:TurbulaFlightList"
    regex = re.compile(
        r"\{\{AstrellaFlight\|imgname = Turbula\|code = LU(?P<code>[^|\n]*?)\|airport1 = (?P<a1>[^|\n]*?)(?:\|gate1 = (?P<g1>[^|\n]*?)|)\|airport2 = (?P<a2>[^|\n]*?)(?:\|gate2 = (?P<g2>[^|\n]*?)|)\|.*?size = (?P<ac>[^|\n]*?)\|status = active}}"
    )


@AIRLINE_SOURCES.append
class BluAir(RegexWikiAirline):
    airline_name = "BluAir"
    page_name = "List of BluAir flights"
    regex = re.compile(
        r"\{\{BA\|BU(?P<code>[^|<]*)[^|]*?\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|(?P<acc>[^|]*?)\|.}}"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        match matches["acc"]:
            case "s4n":
                return "BluJet S4-N"
            case "s4h":
                return "BluJet S4-H"
            case "m1":
                return "BluJet M1"
            case "ms2":
                return "BluJet MS2"
            case "l1":
                return "BluJet L1"
            case other:
                raise ValueError(other)


@AIRLINE_SOURCES.append
class IntraAir(AirSource):
    name = "MRT Wiki (Airline IntraAir)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("IntraAir/Flight List", config)

    def build(self, config: Config):
        airline = self.airline(name="IntraAir", link=get_wiki_link("IntraAir/Flight List"))

        for table in self.html("table"):
            for tr in table("tr")[1:]:
                if len(tr("td")) < 9:
                    continue
                if tr("td")[8].find("a", href="/index.php/File:CaelusAirlines_Boarding.png") is None:
                    continue
                flight_code = tr("td")[1].span.string
                airport1_code = tr("td")[2].span.string
                airport2_code = tr("td")[4].span.string

                g1 = tr("td")[3]("b")[1:]
                gate1_code = (
                    None if len(g1) == 0 else g1[0].string if len(g1) == 1 else f"T{g1[0].string}-{g1[1].string}"
                )

                g2 = tr("td")[5]("b")[1:]
                gate2_code = (
                    None if len(g2) == 0 else g2[0].string if len(g2) == 1 else f"T{g2[0].string}-{g2[1].string}"
                )

                aircraft_name = tr("td")[6].span.string

                self.connect(
                    airline=airline,
                    flight_code1=flight_code,
                    flight_code2=flight_code,
                    airport1_code=airport1_code,
                    airport2_code=airport2_code,
                    gate1_code=gate1_code,
                    gate2_code=gate2_code,
                    aircraft_name=aircraft_name,
                )


@AIRLINE_SOURCES.append
class FliHigh(AirSource):
    name = "MRT Wiki (Airline FliHigh)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("FliHigh Airlines", config)

    def build(self, config: Config):
        airline = self.airline(name="FliHigh Airlines", link=get_wiki_link("FliHigh Airlines"))

        for table in self.html("table"):
            if table.find(string="Flight #") is None:
                continue
            for tr in table("tr")[1:]:
                if tr("td")[7].find("a", href="/index.php/File:Open.png") is None:
                    continue
                flight_code = tr("td")[0].find("span").string.removeprefix("FH")
                airport1_code = tr("td")[1].b.string
                airport2_code = tr("td")[2].b.string
                gate1_code = tr("td")[5].b.string
                gate2_code = tr("td")[6].b.string
                if "idk" in gate1_code or "CHECK WIKI" in gate1_code:
                    gate1_code = None
                if "idk" in gate2_code or "CHECK WIKI" in gate2_code:
                    gate2_code = None
                aircraft_name = tr("td")[8].string.strip()

                self.connect(
                    airline=airline,
                    flight_code1=flight_code,
                    flight_code2=flight_code,
                    airport1_code=airport1_code,
                    airport2_code=airport2_code,
                    gate1_code=gate1_code,
                    gate2_code=gate2_code,
                    aircraft_name=aircraft_name,
                )


@AIRLINE_SOURCES.append
class AirMesa(RegexWikiAirline):
    airline_name = "AirMesa"
    page_name = "AirMesa"
    regex = re.compile(
        r"\{\{BA\|AM(?P<code>[^|]*?)\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|(?P<acc>[^|]*?)\|..}}"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        match matches["acc"]:
            case "p1":
                return "Moj Manufacturing P-1MJ"
            case other:
                raise ValueError(other)


@AIRLINE_SOURCES.append
class Air(RegexWikiAirline):
    airline_name = "air"
    page_name = "Template:Air"
    regex = re.compile(
        r"\{\{BA\|↑↑(?P<code>[^|]*?)\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|(?P<acc>[^|]*?)\|..}}"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        match matches["acc"]:
            case "frs":
                return "\"Fred Rail Air' Compact Surveillance Aircraft"
            case other:
                raise ValueError(other)


@AIRLINE_SOURCES.append
class Berryessa(RegexWikiAirline):
    airline_name = "Berryessa Airlines"
    page_name = "Berryessa Airlines"
    regex = re.compile(
        r"\{\{BA\|IN(?P<code>[^|<]*)[^|]*?\|(?P<a1>[^|]*?)\|(?P<a2>[^|]*?)\|[^|]*?\|[^|]*?\|(?P<g1>[^|]*?)\|(?P<g2>[^|]*?)\|a\|(?P<acc>[^|]*?)\|..}}"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        match matches["acc"]:
            case "747":
                return "SkyTransit 747-8"
            case "50":
                return "EAM X-50"
            case "10":
                return "EAM X-10"
            case "15":
                return "EAM X-15"
            case "tini":
                return "IntraJet 4G Tini 4.0"
            case "318":
                return "Infamous A318"
            case other:
                raise ValueError(other)


@AIRLINE_SOURCES.append
class AirNet(AirSource):
    name = "MRT Wiki (Airline AirNet)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("AirNet", config)

    def build(self, config: Config):
        airline = self.airline(name="AirNet", link=get_wiki_link("AirNet"))

        table = next(a for a in self.html("table") if "Number" in str(a))
        for tr in table.tbody("tr")[1:]:
            if "Boarding" not in str(tr("td")[3]):
                continue
            flight_code = next(tr("td")[0].strings).removeprefix("AN")
            ng1 = "".join(tr("td")[1].strings)
            ng2 = "".join(tr("td")[2].strings)
            airport1_name, gate1_code = ng1.split("|")
            airport2_name, gate2_code = ng2.split("|")

            self.connect(
                airline=airline,
                flight_code1=flight_code,
                flight_code2=flight_code,
                airport1_name=airport1_name,
                airport2_name=airport2_name,
                gate1_code=gate1_code,
                gate2_code=gate2_code,
            )


@AIRLINE_SOURCES.append
class FlyCreeper(AirSource):
    name = "MRT Wiki (Airline FlyCreeper)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("FlyCreeper", config)

    def build(self, config: Config):
        airline = self.airline(name="FlyCreeper", link=get_wiki_link("FlyCreeper"))

        for table in self.html("table"):
            if "Flight No" not in str(table):
                continue
            for tr in table.tbody("tr")[1:]:
                if "Active" not in tr("td")[2].string:
                    continue
                flight_code = tr("td")[0].string.removeprefix("FC").strip()
                if (airport1_code := re.search(r"\((...)\)", str(tr("td")[3]("b")[0]))) is None:
                    continue
                airport1_code = airport1_code.group(1)
                if (airport2_code := re.search(r"\((...)\)", str(tr("td")[3]("b")[1]))) is None:
                    continue
                airport2_code = airport2_code.group(1)
                gate1_code, gate2_code = list(tr("td")[4].strings)[:2]
                aircraft_name = tr("td")[6].string.strip()
                self.connect(
                    airline=airline,
                    flight_code1=flight_code,
                    flight_code2=flight_code,
                    airport1_code=airport1_code,
                    airport2_code=airport2_code,
                    gate1_code=gate1_code,
                    gate2_code=gate2_code,
                    aircraft_name=aircraft_name,
                )


@AIRLINE_SOURCES.append
class Continental(RegexWikiAirline):
    airline_name = "Continental Airlines"
    page_name = "Continental Airlines"
    regex = re.compile(
        r"\|-\n\|.*?\n\|(?:CO)?(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|(?P<g1>[^|]*?)\n\|(?P<g2>[^|]*?)\n\|{{status\|good}}\n\|(?P<ac2>.*?)\n",
        re.IGNORECASE,
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        if matches["ac2"].strip() == "IntraJet-EAM X-10":
            return "EAM X-10"
        return matches["ac2"].strip()


@AIRLINE_SOURCES.append
class AirKanata(RegexWikiAirline):
    airline_name = "Air Kanata"
    page_name = "Air Kanata"
    regex = re.compile(
        r"\|-\n\|AK(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}} ?\n\|'''.*?'''(?:\n|<br ?/>|)(?P<ac2>.*?)\n"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        name = matches["ac2"].strip()
        if name == "Dash Two Mini":
            return "UDAC Dash Two Mini"
        return name


@AIRLINE_SOURCES.append
class JiffyAir(RegexWikiAirline):
    airline_name = "JiffyAir"
    page_name = "JiffyAir"
    regex = re.compile(
        r"\|-\n\|JF(?P<code>[^|]*?)\n\|(?:{{afn\|(?P<a1>[^|]*?)}}|.*?\((?P<a12>[^|]*?)\))\n\|(?:{{afn\|(?P<a2>[^|]*?)}}|.*?\((?P<a22>[^|]*?)\))\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}\n\|'''(?P<ac1>.*?)''' (?P<ac2>.*?)<"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        return matches["ac1"] + " " + matches["ac2"]


@AIRLINE_SOURCES.append
class Tennoji(RegexWikiAirline):
    airline_name = "Tennoji Airways"
    page_name = "Tennoji Airways"
    regex = re.compile(
        r"\|-\n\|(?:TA|RK)(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}\n\|''(?P<ac1>.*?)'' (?P<ac2>.*?)\n"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        return matches["ac1"] + " " + matches["ac2"]

    @staticmethod
    def mode(matches: dict[str, str]) -> str | None:
        return "helicopter" if matches["code"].startswith("H") else "warp plane"


@AIRLINE_SOURCES.append
class Yousoro(RegexWikiAirline):
    airline_name = "Yousoro!"
    page_name = "Yousoro!"
    regex = re.compile(
        r"\|-\n\|RKS(?P<code>[^|]*?)\n\|'''(?P<a1>[^|]*?)'''.*?\n\|'''(?P<a2>[^|]*?)'''.*?\n\|'''(?P<g1>[^|]*?)'''\n\|'''(?P<g2>[^|]*?)'''\n\|{{[sS]tatus\|good}}\n\|''(?P<ac1>.*?)'' (?P<ac2>.*?)\n"
    )

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        return matches["ac1"] + " " + matches["ac2"]

    @staticmethod
    def mode(_matches: dict[str, str]) -> gt.AirMode | None:
        return "seaplane"


@AIRLINE_SOURCES.append
class RainerAirways(RegexWikiAirline):
    airline_name = "Rainer Airways"
    page_name = "Rainer Airways"
    regex = re.compile(
        r"""\|-
\|RB(?P<code>.*?)
\|(?:{{afn\|(?P<a1>.*?)}}|.*?\((?P<a12>.*?)\))
\|(?P<g1>.*?)
\|(?:{{afn\|(?P<a2>.*?)}}|.*?\((?P<a22>.*?)\))
\|(?P<g2>.*?)
"""
    )

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        return "seaplane" if matches["code"].startswith("S") else "helicopter" if matches["code"].startswith("H") else "warp plane"


@AIRLINE_SOURCES.append
class MarbleAir(RegexWikiAirline):
    airline_name = "MarbleAir"
    page_name = "MarbleAir"
    regex = re.compile(
            r"\|-\n\|'''MA(?P<code>.*?)'''\n.*?\n\|.*?\((?P<a1>.*?)\)\n\|.*?\((?P<a2>.*?)\)\n\|(?P<ac>.*?)\n\|Active"
    )

    @staticmethod
    def process_flight_code_back(code: str) -> str:
        return str(int(code) + 1)


@AIRLINE_SOURCES.append
class AmberAir(RegexWikiAirline):
    airline_name = "AmberAir"
    page_name = "AmberAir"
    regex = re.compile(r"""\|-
\|'''AB(?P<code>.*?)/.*?'''
\|'''(?:\[\[.*?\|(?P<a1>[^|]*?)]]|(?P<a12>[^|']*))'''.*?
'''to (?:\[\[.*?\|(?P<a2>[^|]*?)]]|(?P<a22>[^|']*))'''.*?
\|(?:'''(?P<g1>[^|]*?)'''|)
\|(?:'''(?P<g2>[^|].*?)'''|)
\|(?P<ac>.*?)
\|\[\[File:Service Good\.png\|50px]]""")

    @staticmethod
    def process_flight_code_back(code: str) -> str:
        return str(int(code) + 1)


@AIRLINE_SOURCES.append
class ArcticAir(AirSource):
    name = "MRT Wiki (Airline ArcticAir)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        self.df = get_csv(
            "https://docs.google.com/spreadsheets/d/1XhIW2kdX_d56qpT-kyGz6tD9ZuPQtqSeFZvPiqMDAVU/export?format=csv&gid=0",
            "arctic_air",
            config,
        )

    def build(self, config: Config):
        airline = self.airline(name="ArcticAir", link=get_wiki_link("ArcticAir"))

        d = list(
            zip(
                self.df["Flight"],
                self.df["Departure"],
                self.df["Arrival"],
                self.df["D. Gate"],
                self.df["A. Gate"],
                strict=False,
            )
        )

        for flight, a1, a2, g1, g2 in d:
            if str(flight).strip() in ("227", "228", "239", "240"):
                continue
            if pd.isna(a1):
                continue

            if str(a1).strip() not in DUPLICATE_GATE_NUM:
                g1 = re.sub(r"T. ", "", str(g1))  # noqa: PLW2901
            if str(a2).strip() not in DUPLICATE_GATE_NUM:
                g2 = re.sub(r"T. ", "", str(g2))  # noqa: PLW2901

            self.connect(
                airline=airline,
                flight_code1=str(flight),
                flight_code2=None,
                airport1_code=a1,
                airport2_code=a2,
                gate1_code=g1 if "*" not in g1 else None,
                gate2_code=g2 if "*" not in g2 else None,
            )


@AIRLINE_SOURCES.append
class SandstoneAirr(AirSource):
    name = "MRT Wiki (Airline SandstoneAirr)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        self.df = get_csv(
            "https://docs.google.com/spreadsheets/d/1XhIW2kdX_d56qpT-kyGz6tD9ZuPQtqSeFZvPiqMDAVU/export?format=csv&gid=3084051",
            "sandstone_airr",
            config,
        )

    def build(self, config: Config):
        airline = self.airline(name="Sandstone Airr", link=get_wiki_link("Sandstone Airr"))

        d = list(zip(self.df["Unnamed: 1"], self.df["Unnamed: 2"], self.df["Airport"], self.df["Gate"], strict=False))

        for (flight1, flight2, a1, g1), (_, _, a2, g2) in list(itertools.pairwise(d))[::2]:
            if pd.isna(a1):
                continue

            if str(a1).strip() not in DUPLICATE_GATE_NUM:
                g1 = re.sub(r"T. ", "", str(g1))  # noqa: PLW2901
            if str(a2).strip() not in DUPLICATE_GATE_NUM:
                g2 = re.sub(r"T. ", "", str(g2))  # noqa: PLW2901

            self.connect(
                airline=airline,
                flight_code1=str(int(flight1)),
                flight_code2=str(int(flight2)),
                airport1_code=a1,
                airport2_code=a2,
                gate1_code=g1 if "*" not in g1 else None,
                gate2_code=g2 if "*" not in g2 else None,
            )


@AIRLINE_SOURCES.append
class Michigana(RegexWikiAirline):
    airline_name = "Michigana"
    page_name = "Template:Michigana"
    regex = re.compile(r"""\|\|<font size="4">'''MI(?P<code>.*?)'''</font>
\|\|<font size="4">'''(?P<a1>.*?)'''</font> <br/>.*?
\|\|.*?
\|\|<font size="4">'''(?P<a2>.*?)'''</font> <br/>.*?
\|\|'''{{color\|gray\|(?P<ac>.*?)}}'''
\|\| \[\[File:Eastern Active1\.png\|50px]]""")


@AIRLINE_SOURCES.append
class Lilyflower(AirSource):
    name = "MRT Wiki (Airline Lilyflower Airlines)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        self.df = get_csv(
            "https://docs.google.com/spreadsheets/d/1B-fSerCAQAtaW-kAfv1npdjpGt-N1PrB1iUOmUBX5HI/export?format=csv&gid=1864111212",
            "lilyflower",
            config,
            header=1,
        )

    def build(self, config: Config):
        airline = self.airline(name="Lilyflower Airlines", link=get_wiki_link("Lilyflower Airlines"))

        d = list(
            zip(self.df["Flight"], self.df["IATA"], self.df["Gate"], self.df["IATA.1"], self.df["Gate.1"], self.df["Plane"], strict=False)
        )

        for flight, a1, g1, a2, g2, aircraft_name in d:
            if pd.isna(a1):
                continue
            self.connect(
                airline=airline,
                flight_code1=str(int(flight)),
                flight_code2=str(int(flight)),
                airport1_code=a1,
                airport2_code=a2,
                gate1_code=g1,
                gate2_code=g2,
                aircraft_name=aircraft_name
            )


@AIRLINE_SOURCES.append
class RodBla(RegexWikiAirline):
    airline_name = "RodBla Heli"
    page_name = "RodBla Heli"
    regex = re.compile(r"\|RB(?P<code>.*?)\n\|Active\n\|(?P<a1>.*?)-(?P<a2>.*?)\n\|(?P<ac>.*?)\n")

    @staticmethod
    def mode(_matches: dict[str, str]) -> gt.AirMode | None:
        return "helicopter"


@AIRLINE_SOURCES.append
class MylesHeli(RegexWikiAirline):
    airline_name = "MylesHeli"
    page_name = "MylesHeli/Flights"
    regex = re.compile(r"{{mylesh\|MY(?P<code>.*?)\|t\|(?P<a1>.*?)\|.*?\|.*?\|(?P<a2>.*?)\|.*?\|.*?}}")

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        if matches["a1"] == "GSA":
            matches["a1"] = "GSAH"
        if matches["a2"] == "GSA":
            matches["a2"] = "GSAH"
        return "helicopter"


@AIRLINE_SOURCES.append
class Aero(RegexWikiAirline):
    airline_name = "aero"
    page_name = "Aero"
    regex = re.compile(r"""\|\|<font size="4">'''ae(?P<code>.*?)'''.*?
\|\|<font size="4">'''(?P<a1>.*?)'''(?:.*?gate (?P<g1>.*?)[)']|).*?
\|\|.*?
\|\|<font size="4">'''(?P<a2>.*?)'''(?:.*?gate (?P<g2>.*?)[)']|).*?
\|\|'''{{color\|black\|(?P<ac>.*?)}}'''
\|\|.*?
\|\|.*?\[\[File:Eastern Active\.gif\|50px]]""")


@AIRLINE_SOURCES.append
class SouthWeast(AirSource):
    name = "MRT Wiki (Airline South Weast Airlines)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("South Weast Airlines", config)

    def build(self, config: Config):
        airline = self.airline(name="South Weast Airlines", link=get_wiki_link("South Weast Airlines"))
        table = next(a for a in self.html("table") if "Flight Number" in str(a))
        for tr in table.tbody("tr")[1:]:
            if "ON TIME" not in str(tr("td")[4]):
                continue
            flight_code = tr("td")[0].string
            airport1_name = "".join(tr("td")[2].strings)
            airport2_name = "".join(tr("td")[3].strings)

            self.connect(
                airline=airline,
                flight_code1=flight_code,
                flight_code2=flight_code,
                airport1_name=airport1_name,
                airport2_name=airport2_name,
                mode="helicopter" if flight_code.startswith("H") else "warp plane",
            )


@AIRLINE_SOURCES.append
class UtopiAir(AirSource):
    name = "MRT Wiki (Airline UtopiAir)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("UtopiAir", config)

    def build(self, config: Config):
        airline = self.airline(name="UtopiAir", link=get_wiki_link("UtopiAir"))

        for table in (a for a in self.html("table") if "Flight" in str(a)):
            for tr in table.tbody("tr")[1:]:
                if len(tr("td")) > 3 and "ON TIME" not in str(tr("td")[3]):
                    continue
                flight_code = tr("td")[0].string
                airport1_name = "".join(tr("td")[1].strings)
                airport2_name = "".join(tr("td")[2].strings)
                if airport1_name == "Porton":
                    airport1_name = "Porton Seaplane Dock"
                if airport2_name == "Porton":
                    airport2_name = "Porton Seaplane Dock"

                self.connect(
                    airline=airline,
                    flight_code1=flight_code,
                    flight_code2=flight_code,
                    airport1_name=airport1_name,
                    airport2_name=airport2_name,
                    mode="seaplane" if int(flight_code) >= 500 else "warp plane",
                )


@AIRLINE_SOURCES.append
class SoutheasternAirways(RegexWikiAirline):
    airline_name = "Southeastern Airways"
    page_name = "Template:Southeastern Airways Flight List"
    regex = re.compile(r"""\|\|.*?'''SE(?P<code>.*?)'''.*?
\|\|.*?'''(?:\[\[.*?\||\[\[)?(?P<a1>.*?)(?:]])?'''.*?
\|\|.*?
\|\|.*?'''(?:\[\[.*?\||\[\[)?(?P<a2>.*?)(?:]])?'''.*?
\|\|\[\[File:Eastern Active\.gif""")


@AIRLINE_SOURCES.append
class Caelus(AirSource):
    name = "MRT Wiki (Airline Caelus Airlines)"
    text0: str
    text1: str
    text2: str
    html3: bs4.BeautifulSoup
    html4: bs4.BeautifulSoup
    text7: str
    regex = re.compile(r"""(?s)\|-
! .*?
! .*?CL (?P<code>.*?)<.*?
! .*?'''(?P<a1>.*?)'''.*?
! .*?'''(?P<a2>.*?)'''.*?
! .*?\| (?P<ac>.*?)
! .*?CaelusAirlines_Boarding\.png""")

    def prepare(self, config: Config):
        self.text0 = get_wiki_text("Template:ICAG 000 Series Flights", config)
        self.text1 = get_wiki_text("Template:ICAG 100 Series Flights", config)
        self.text2 = get_wiki_text("Template:ICAG 200 Series Flights", config)
        self.html3 = get_wiki_html("Template:ICAG 300 Series Flights", config)
        self.html4 = get_wiki_html("Template:ICAG 400 Series Flights", config)
        self.text7 = get_wiki_text("Template:ICAG 700 Series Flights", config)

    def build(self, config: Config):
        airline = self.airline(name="Caelus Airlines", link=get_wiki_link("Caelus Airlines"))

        for text in (self.text0, self.text1, self.text2, self.text7):
            for match in re.finditer(self.regex, text):
                self.connect(
                    airline=airline,
                    flight_code1=match["code"],
                    flight_code2=str(int(match["code"]) + 1),
                    airport1_code=match["a1"],
                    airport2_code=match["a2"],
                    aircraft_name=None if match["ac"].strip() == "" else match["ac"].split(" (")[0],
                )

        table = next(a for a in self.html3("table") if "Operated by" in str(a))
        for tr in table.tbody("tr")[1:]:
            if "CaelusAirlines_Boarding.png" not in str(tr("td")[4]):
                continue
            code1, code2 = tr("td")[1].string.removeprefix("Flight ").split("/")
            a1, a2 = (b.string for b in tr("td")[2]("b"))
            aircraft_name = tr("td")[3].string
            self.connect(
                airline=airline,
                flight_code1=code1,
                flight_code2=code2,
                airport1_code=a1,
                airport2_code=a2,
                aircraft_name=aircraft_name
            )

        table = next(a for a in self.html4("table") if "Operated by" in str(a))
        for tr in table.tbody("tr")[1:]:
            if "CaelusAirlines_Boarding.png" not in str(tr("td")[4]):
                continue
            code1, code2 = tr("td")[1].string.removeprefix("Flight ").split("/")
            n1, n2 = tr("td")[2].strings
            if n1 == "Deadbush Northeast Airfield":
                n1 = "West Mesa International Airport"
            if n2 == "Deadbush Northeast Airfield":
                n2 = "West Mesa International Airport"
            self.connect(
                airline=airline,
                flight_code1=code1,
                flight_code2=code2,
                airport1_name=n1,
                airport2_name=n2,
                mode="helicopter",
            )


@AIRLINE_SOURCES.append
class CBC(RegexWikiAirline):
    airline_name = "Caravacan Biplane Company"
    page_name = "Caravacan Biplane Company"
    regex = re.compile(r"""(?P<code>.*?)\. (?P<a1>.*?) --- (?P<a2>.*?) /""")

    @staticmethod
    def aircraft(_matches: dict[str, str]) -> str | None:
        return "Caravacan Biplane"


@AIRLINE_SOURCES.append
class Cascadia(RegexWikiAirline):
    airline_name = "Cascadia Airways"
    page_name = "Template:CascadiaAirGroupCA"
    regex = re.compile(r"""\|- ?
! .*?
\|.*?
\|\|.*?'''CA (?P<code>.*?)'''.*?
\|\|.*?'''(?P<a1>.*?)(?: & (?P<a3>.*?))?'''.*?
\|\|.*?
\|\|.*?'''(?P<a2>.*?)'''.*?
\|\| '''{{color\|gray\|(?P<ac2>.*?)}}'''
\|\| \[\[File:Eastern Active1\.png""")

    @staticmethod
    def aircraft(matches: dict[str, str]) -> str | None:
        return matches["ac2"].strip().replace("P1315", "P 1315").replace("<br>", " ").replace("<small>", "").replace("</small>", "")


@AIRLINE_SOURCES.append
class Waviation(AirSource):
    name = "MRT Wiki (Airline Waviation)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("Waviation", config)

    def build(self, config: Config):
        airline = self.airline(name="Waviation", link=get_wiki_link("Waviation"))

        for table in self.html("table"):
            if (caption := table.find("caption")) is None or (
                "(000s)" not in str(caption) and "(1000s)" not in str(caption)
            ):
                continue

            if "(000s)" in str(caption) or "(2000s)" in str(caption):
                for tr in table.tbody("tr")[1:]:
                    if "N/A" not in str(tr("td")[7]):
                        continue
                    code1, code2 = tr("td")[0].string.split("/")
                    a1 = tr("td")[1].b.string
                    g1 = tr("td")[2].string
                    a2 = tr("td")[3].b.string
                    g2 = tr("td")[4].string
                    if "XX" in g1:
                        g1 = None
                    if "XX" in g2:
                        g2 = None
                    aircraft_name = tr("td")[5].string
                    self.connect(
                        airline=airline,
                        flight_code1=code1,
                        flight_code2=code2,
                        airport1_code=a1,
                        airport2_code=a2,
                        gate1_code=g1,
                        gate2_code=g2,
                        aircraft_name=aircraft_name
                    )
            elif "(1200s)" in str(caption):
                for tr in table.tbody("tr")[1:]:
                    if "N/A" not in str(tr("td")[6]):
                        continue
                    code1, code2 = tr("td")[0].string.split("/")
                    a1 = tr("td")[1].b.string
                    a2 = tr("td")[2].b.string
                    g2 = tr("td")[3].string
                    if "XX" in g2:
                        g2 = None
                    aircraft_name = tr("td")[4].string
                    self.connect(
                        airline=airline,
                        flight_code1=code1,
                        flight_code2=code2,
                        airport1_code=a1,
                        airport2_code=a2,
                        gate1_code=None,
                        gate2_code=g2,
                        aircraft_name=aircraft_name,
                    )
            else:
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
                    code1, code2 = tr("td")[0].string.split("/")
                    g1 = tr("td")[1].string
                    a2 = tr("td")[2].b.string
                    g2 = tr("td")[3].string
                    if "XX" in g1:
                        g1 = None
                    if "XX" in g2:
                        g2 = None
                    aircraft_name = tr("td")[4].string
                    self.connect(
                        airline=airline,
                        flight_code1=code1,
                        flight_code2=code2,
                        airport1_code=a1,
                        airport2_code=a2,
                        gate1_code=g1,
                        gate2_code=g2,
                        aircraft_name=aircraft_name,
                    )
