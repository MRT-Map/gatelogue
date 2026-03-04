from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pandas as pd

import gatelogue_types as gt
from gatelogue_aggregator.downloader import get_csv, get_wiki_html, get_wiki_link
from gatelogue_aggregator.source import AirSource
from gatelogue_aggregator.sources.air.wiki_airport import RegexWikiAirport

if TYPE_CHECKING:
    import bs4

    from gatelogue_aggregator.config import Config

AIRPORT_SOURCES: list[type[AirSource]] = []


@AIRPORT_SOURCES.append
class PCE(RegexWikiAirport):
    airport_code = "PCE"
    page_name = "Peacopolis International Airport"
    regex = re.compile(
        r"(?s)\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*?|)\|\|(?:(?!Service).)*Service"
    )

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        code = matches["code"]
        return 39 if code.startswith(("D", "E", "F")) else 15


@AIRPORT_SOURCES.append
class MWT(RegexWikiAirport):
    airport_code = "MWT"
    page_name = "Miu Wan Tseng Tsz Leng International Airport"
    regex = re.compile(r"\|-\n\|(?P<code>[PD]?\d*?A?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>.*?)\n|\n)")

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        code = matches["code"].removesuffix("A")
        return None if code.startswith("D") else 9 if code.startswith("P") else 11 if 83 <= int(code) <= 103 else 41 if 61 <= int(code) <= 68 else 33 if 69 <= int(code) <= 76 else 15

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        code = matches["code"]
        if code.isdigit() and 83 <= int(code) <= 103:
            return "helicopter"
        return "warp plane"


@AIRPORT_SOURCES.append
class KEK(RegexWikiAirport):
    airport_code = "KEK"
    page_name = "Kazeshima Eumi Konaejima Airport"
    regex = re.compile(r"\|(?P<code>[^|}]*?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)\|\|")

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        return 11 if int(matches["code"]) > 100 else None

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        return "warp plane" if int(matches["code"]) > 100 else "seaplane"


@AIRPORT_SOURCES.append
class ABG(RegexWikiAirport):
    airport_code = "ABG"
    page_name = "Antioch-Bay Point Garvey International Airport"
    regex = re.compile(
        r"\|(?P<code>.*?\d)\|\| ?(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)(?:\|\||\n)",
    )

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        return 43 if matches["code"].startswith(("I", "J")) else 15


@AIRPORT_SOURCES.append
class OPA(RegexWikiAirport):
    airport_code = "OPA"
    page_name = "Oparia LeTourneau International Airport"
    regex = re.compile(
        r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
    )

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        code = matches["code"]
        return 39 if code.startswith("C") and 1 <= int(code.removeprefix("C")) <= 4 else 15


@AIRPORT_SOURCES.append
class CHB(RegexWikiAirport):
    airport_code = "CHB"
    page_name = "Chan Bay Municipal Airport"
    regex = re.compile(
        r"\|Gate (?P<code>.*?)\n\|.\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
    )

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        return 33 if matches["code"].isdigit() and int(matches["code"]) >= 25 else 15

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        return "helicopter" if matches["code"].startswith("H") else "warp plane"


@AIRPORT_SOURCES.append
class CBZ(RegexWikiAirport):
    airport_code = "CBZ"
    page_name = "Chan Bay Zeta Airport"
    regex = re.compile(r"\|(?P<code>[AB]\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)")

    @staticmethod
    def width(_matches: dict[str, str]) -> int | None:
        return 15


@AIRPORT_SOURCES.append
class CBI(RegexWikiAirport):
    airport_code = "CBI"
    page_name = "Chan Bay International Airport"
    regex = re.compile(r"\|(?P<code>\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)")

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        return 41 if int(matches["code"]) >= 18 else 15


@AIRPORT_SOURCES.append
class DJE(AirSource):
    name = "MRT Wiki (Airport DJE)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("Deadbush Johnston-Euphorial Airport", config)

    def build(self, config: Config):
        airport = self.airport(
            code="DJE",
            names={"Deadbush Johnston-Euphorial Airport"},
            link=get_wiki_link("Deadbush Johnston-Euphorial Airport"),
        )

        for table in self.html("table"):
            if (caption := table.caption.string.strip() if table.caption is not None else None) is None:
                continue
            if caption == "Terminal 1":
                for tr in table("tr")[1:]:
                    code = tr("td")[0].string
                    width = 31 if 1 <= int(code) <= 10 else 15
                    airline = tr("td")[1]
                    airline = airline.a.string if airline.a is not None else airline.string
                    airline = airline if airline is not None and airline.strip() != "" else None
                    self.gate(
                        code=code,
                        airport=airport,
                        airline=None if airline is None else self.airline(name=airline),
                        width=width
                    )
            elif caption == "Terminal 2":
                concourse = ""
                for tr in table("tr")[1:]:
                    if len(tr("td")) == 1:
                        concourse = tr.find("b").string.strip(" ")[0]
                        continue
                    code = concourse + tr("td")[0].string
                    airline = tr("td")[1]
                    airline = airline.a.string if airline.a is not None else airline.string
                    airline = airline if airline is not None and airline.strip() != "" else None
                    self.gate(
                        code=code,
                        airport=airport,
                        airline=None if airline is None else self.airline(name=airline),
                        width=15,
                    )


@AIRPORT_SOURCES.append
class VDA(RegexWikiAirport):
    airport_code = "VDA"
    page_name = "Deadbush Valletta Desert Airport"
    regex = re.compile(r"\|(?P<code>\d+?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)")

    @staticmethod
    def width(_matches: dict[str, str]) -> int | None:
        return 15


@AIRPORT_SOURCES.append
class WMI(RegexWikiAirport):
    airport_code = "WMI"
    page_name = "West Mesa International Airport"
    regex = re.compile(r"\|Gate (?P<code>.*?)\n\| (?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)")

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        return 39 if matches["code"].startswith("I") and matches["code"] not in ("I14", "I15", "I16") else 15


@AIRPORT_SOURCES.append
class DFM(RegexWikiAirport):
    airport_code = "DFM"
    page_name = "Deadbush Foxfoe Memorial Airport"
    regex = re.compile(
        r"\|Gate (?P<code>.*?)\n\|(?P<size>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)\n|[^|]*?)"
    )

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        code = int(matches["code"])
        return 35 if code in (1, 2, 3, 13, 14, 15) else 31 if 65 <= code <= 71 else 17 if code in (72, 73, 35, 36, 37, 62, 63, 64) else 15

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        code = int(matches["code"])
        return "helicopter" if code in (72, 73, 35, 36, 37, 62, 63, 64) else "warp plane"


@AIRPORT_SOURCES.append
class DBI(AirSource):
    name = "MRT Wiki (Airport DBI)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("Deadbush International Airport", config)

    def build(self, config: Config):
        airport = self.airport(
            code="DBI", names={"Deadbush International Airport"}, link=get_wiki_link("Deadbush International Airport")
        )

        for table in self.html("table"):
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
                width = 39 if size == "M" else 17 if size == "S" else None
                airline = tr("td")[2]
                airline = airline.a.string if airline.a is not None else airline.string
                self.gate(
                    code=code,
                    airport=airport,
                    airline=None if airline is None else self.airline(name=airline),
                    width=width,
                    mode="warp plane"
                )


@AIRPORT_SOURCES.append
class GSM(RegexWikiAirport):
    airport_code = "GSM"
    page_name = "Gemstride Melodia Airfield"
    regex = re.compile(
        r"\|(?P<code>.*?)\n\|'''(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>[^N]\S[^|]*)|[^|]*?)'''"
    )

    @staticmethod
    def width(_matches: dict[str, str]) -> int | None:
        return 13

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        return "helicopter" if matches["code"].startswith("H") else "warp plane"


@AIRPORT_SOURCES.append
class VFW(RegexWikiAirport):
    airport_code = "VFW"
    page_name = "Venceslo-Fifth Ward International Airport"
    regex = re.compile(
        r"\|-\n\|(?P<code>\w*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*|(?P<airline2>\S[^|]*)|[^|]*?)\n\|"
    )


@AIRPORT_SOURCES.append
class SDZ(RegexWikiAirport):
    airport_code = "SDZ"
    page_name = "San Dzobiak International Airport"
    regex = re.compile(
        r"\|-\n\|'''(?P<code>\w*?)'''\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*|(?P<airline2>(?!vacant)\S[^|]*)|[^|]*?)\n\|",
    )

    @staticmethod
    def width(_matches: dict[str, str]) -> int | None:
        return 15


@AIRPORT_SOURCES.append
class CIA(RegexWikiAirport):
    airport_code = "CIA"
    page_name = "Carnoustie International Airport"
    regex = re.compile(
        r"\|\s*(?P<code>.*?)\s*\|\|\s*(?:\[\[(?P<airline>[^|]*?)]]|(?P<airline2>[^|]*?))\s*\|\|",
    )

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        code = matches["code"]
        return "helicopter" if code.startswith("H") else "warp plane"

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        code = matches["code"]
        return 43 if code.startswith(("A", "B")) else 59 if code.startswith("E") else 15


@AIRPORT_SOURCES.append
class ERZ(RegexWikiAirport):
    airport_code = "ERZ"
    page_name = "Erzgard International Airport"
    regex = re.compile(
        r"\|-\n\|(?P<code>.*?)\n\|(?P<size>.).*?\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
    )

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        code = matches["code"]
        return 39 if code in ("A10", "A11", "A12", "B11", "B12") else 15

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        return "helicopter" if matches["code"].startswith("H") else "warp plane"


@AIRPORT_SOURCES.append
class ERZ2(RegexWikiAirport):
    airport_code = "ERZ"
    page_name = "Erzville Passenger Seaport"
    regex = re.compile(
        r"\|-\n\|(?P<code>S.*?)\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
    )

    @staticmethod
    def mode(_matches: dict[str, str]) -> gt.AirMode | None:
        return "seaplane"


@AIRPORT_SOURCES.append
class ATC(RegexWikiAirport):
    airport_code = "ATC"
    page_name = "Achowalogen Takachsin-Covina International Airport"
    regex = re.compile(
        r"\|-\n\|\s*(?P<code>[^|]*?)\s*\|\|[^|]*?\|\|\s*(?:\[\[(?P<airline>[^|]*?)(?:\|[^]]*?|)]][^|]*?|(?P<airline2>[^-|]*?)|-*?)\s*\|\|",
    )

    @staticmethod
    def width(matches: dict[str, str]) -> int | None:
        code = matches["code"]
        return 67 if code in ("W9", "W10", "E9", "E10") else 49 if code.startswith(("N", "S", "E", "W")) else 25 if code.startswith("H") else None

    @staticmethod
    def mode(matches: dict[str, str]) -> gt.AirMode | None:
        code = matches["code"]
        return "helicopter" if code.startswith("H") else "warp plane"


@AIRPORT_SOURCES.append
class AIX(AirSource):
    name = "MRT Wiki (Airport AIX)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        self.df = get_csv(
            "https://docs.google.com/spreadsheets/d/1vG_oEj_XzZlckRwxn4jKkK1FcgjjaULpt66XcxClqP8/export?format=csv&gid=0",
            "aix",
            config,
            header=1,
        )

    def build(self, config: Config):
        airport = self.airport(
            code="AIX", names={"Aurora International Airport"}, link=get_wiki_link("Aurora International Airport")
        )

        d = list(zip(self.df["Gate ID"], self.df["Gate Size"], self.df["Company"], strict=False))

        old_gate_width = None
        for gate_code, gate_size, airline in d:
            if pd.isna(gate_size):
                gate_width = old_gate_width  # noqa: PLW2901
            else:
                gate_size = str(gate_size).strip()
                gate_width = 45 if gate_size == "Large" else 33 if gate_size == "Medium" else 15
                old_gate_width = gate_width
            self.gate(
                code=gate_code,
                airport=airport,
                airline=self.airline(name=airline) if pd.notna(airline) and airline != "Unavailable" else None,
                width=gate_width
            )


@AIRPORT_SOURCES.append
class LAR(AirSource):
    name = "MRT Wiki (Airport LAR)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        self.df = get_csv(
            "https://docs.google.com/spreadsheets/d/1TjGME8Hx_Fh5F0zgHBBvAj_Axlyk4bztUBELiEu4m-w/export?format=csv&gid=0",
            "lar",
            config,
        )

    def build(self, config: Config):
        airport = self.airport(
            code="LAR",
            names={"Larkspur Lilyflower International Airport"},
            link=get_wiki_link("Larkspur Lilyflower International Airport"),
        )

        d = list(zip(self.df["Gate"], self.df["Size"], self.df["Airline"], self.df["Status"], strict=False))

        for gate_code, size, airline, _status in d:
            self.gate(
                code=gate_code,
                airport=airport,
                airline=self.airline(name=airline) if pd.notna(airline) and airline != "?" else None,
                width=41 if size == "M" else 15 if size in ("S", "H") else None,
                mode="helicopter" if size == "H" else "warp plane",
            )


@AIRPORT_SOURCES.append
class LFA(AirSource):
    name = "MRT Wiki (Airport LFA)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        self.df = get_csv(
            "https://docs.google.com/spreadsheets/d/1TjGME8Hx_Fh5F0zgHBBvAj_Axlyk4bztUBELiEu4m-w/export?format=csv&gid=1289412824",
            "lfa",
            config,
        )

    def build(self, config: Config):
        airport = self.airport(
            code="LFA", names={"Larkspur Frankford Airfield"}, link=get_wiki_link("Larkspur Frankford Airfield")
        )

        d = list(zip(self.df["Gate"], self.df["Size"], self.df["Airline"], self.df["Status"], strict=False))

        for gate_code, size, airline, _status in d:
            self.gate(
                code=gate_code,
                airport=airport,
                airline=self.airline(name=airline) if pd.notna(airline) and airline != "?" else None,
                width=15 if size == "S" else None,
            )


@AIRPORT_SOURCES.append
class KWT(RegexWikiAirport):
    airport_code = "KWT"
    page_name = "Ha Shan - Kwai Tin Airport"
    regex = re.compile(r"\|.*?\| \[\[(?P<airline>.*?)]] \|\|.*?\|.*?\|\|.*?\|(?P<code>.*?)\|\|")
    additional_names = {"Kwai Tin Airfield"}

    @staticmethod
    def width(_matches: dict[str, str]) -> int | None:
        return 15


@AIRPORT_SOURCES.append
class SWH(AirSource):
    name = "Gatelogue"

    def build(self, config: Config):
        self.airport(
            code="SWH", names={"Southwold International Airport"}, link=get_wiki_link("Southwold International Airport")
        )


@AIRPORT_SOURCES.append
class EXH(AirSource):
    name = "Gatelogue"

    def build(self, config: Config):
        self.airport(
            code="EXH", names={"Essex Municipal Helport", "Essex Heliport"}, link=get_wiki_link("Essex Heliport")
        )
