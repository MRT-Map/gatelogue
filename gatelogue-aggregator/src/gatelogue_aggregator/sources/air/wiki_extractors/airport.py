from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

import bs4
import pandas as pd

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.source import AirSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html, get_wiki_link
from gatelogue_aggregator.sources.air.wiki_airport import RegexWikiAirport

if TYPE_CHECKING:
    from collections.abc import Callable

    from gatelogue_aggregator.config import Config

AIRPORT_SOURCES: list[type[AirSource]] = []


@AIRPORT_SOURCES.append
class PCE(RegexWikiAirport):
    airport_code = "PCE"
    page_name = "Peacopolis International Airport"
    regex = re.compile(
        r"(?s)\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]].*?|)\|\|(?:(?!Service).)*Service"
    )

@AIRPORT_SOURCES.append
class MWT(RegexWikiAirport):
    airport_code = "MWT"
    page_name = "Miu Wan Tseng Tsz Leng International Airport"
    regex = re.compile(r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|\n)")

    @staticmethod
    def size(matches: dict[str, str]) -> str | None:
        return "XS" if (code := matches["code"].removesuffix("A")).startswith("P") else "S" if int(code) <= 60 else "M" if int(code) <= 82 else "H"


@AIRPORT_SOURCES.append
class KEK(RegexWikiAirport):
    airport_code = "KEK"
    page_name = "Kazeshima Eumi Konaejima Airport"
    regex = re.compile(r"\|(?P<code>[^|}]*?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)\|\|")

    @staticmethod
    def size(matches: dict[str, str]) -> str | None:
        return "XS" if int(matches["code"]) > 100 else "SP"

@AIRPORT_SOURCES.append
class ABG(RegexWikiAirport):
    airport_code = "ABG"
    page_name = "Antioch-Bay Point Garvey International Airport"
    regex = re.compile(
        r"\|(?P<code>.*?\d)\|\| ?(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)(?:\|\||\n)",
    )

@AIRPORT_SOURCES.append
class OPA(RegexWikiAirport):
    airport_code = "OPA"
    page_name = "Oparia LeTourneau International Airport"
    regex = re.compile(
        r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
    )

@AIRPORT_SOURCES.append
class CHB(RegexWikiAirport):
    airport_code = "CHB"
    page_name = "Chan Bay Municipal Airport"
    regex = re.compile(
        r"\|Gate (?P<code>.*?)\n\|.\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)",
    )

@AIRPORT_SOURCES.append
class CBZ(RegexWikiAirport):
    airport_code = "CBZ"
    page_name = "Chan Bay Zeta Airport"
    regex = re.compile(r"\|(?P<code>[AB]\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)")

    @staticmethod
    def size(_matches: dict[str, str]) -> str | None:
        return "S"

@AIRPORT_SOURCES.append
class CBI(RegexWikiAirport):
    airport_code = "CBI"
    page_name = "Chan Bay International Airport"
    regex = re.compile(r"\|(?P<code>\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)")


@AIRPORT_SOURCES.append
class DJE(AirSource):
    name = "MRT Wiki (Airport DJE)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("Deadbush Johnston-Euphorial Airport", config)

    def build(self, config: Config):
        airport = self.airport(code="DJE", names={"Deadbush Johnston-Euphorial Airport"}, link=get_wiki_link("Deadbush Johnston-Euphorial Airport"))

        for table in self.html("table"):
            if (caption := table.caption.string.strip() if table.caption is not None else None) is None:
                continue
            if caption == "Terminal 1":
                for tr in table("tr")[1:]:
                    code = tr("td")[0].string
                    size = "MS" if 1 <= int(code) <= 10 else "S"
                    airline = tr("td")[1]
                    airline = airline.a.string if airline.a is not None else airline.string
                    airline = airline if airline is not None and airline.strip() != "" else None
                    self.gate(code=code, airport=airport, airline=None if airline is None else self.airline(name=airline), size=size)
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
                    self.gate(code=code, airport=airport, airline=None if airline is None else self.airline(name=airline), size=size)

@AIRPORT_SOURCES.append
class VDA(RegexWikiAirport):
    airport_code = "VDA"
    page_name = "Deadbush Valletta Desert Airport"
    regex = re.compile(r"\|(?P<code>\d+?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)")

@AIRPORT_SOURCES.append
class WMI(RegexWikiAirport):
    airport_code = "WMI"
    page_name = "West Mesa International Airport"
    regex = re.compile(r"\|Gate (?P<code>.*?)\n\| (?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|[^|]*?)")

@AIRPORT_SOURCES.append
class DFM(RegexWikiAirport):
    airport_code = "DFM"
    page_name = "Deadbush Foxfoe Memorial Airport"
    regex = re.compile(
        r"\|Gate (?P<code>.*?)\n\|(?P<size>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>\S[^|]*)\n|[^|]*?)"
    )


@AIRPORT_SOURCES.append
class DBI(AirSource):
    name = "MRT Wiki (Airport DBI)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("Deadbush International Airport", config)

    def build(self, config: Config):
        airport = self.airport(code="DBI", names={"Deadbush International Airport"}, link=get_wiki_link("Deadbush International Airport"))

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
                airline = tr("td")[2]
                airline = airline.a.string if airline.a is not None else airline.string
                self.gate(code=code, airport=airport, airline=None if airline is None else self.airline(name=airline), size=size)

@AIRPORT_SOURCES.append
class GSM(RegexWikiAirport):
    airport_code = "GSM"
    page_name = "Gemstride Melodia Airfield"
    regex = re.compile(
        r"\|(?P<code>.*?)\n\|'''(?:\[\[(?:[^|\]]*?\|)?(?P<airline>[^|]*?)]]|(?P<airline2>[^N]\S[^|]*)|[^|]*?)'''"
    )

    @staticmethod
    def size(matches: dict[str, str]) -> str | None:
        return "H" if matches["code"].startswith("H") else "S"

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
    def size(_matches: dict[str, str]) -> str | None:
        return "S"

@AIRPORT_SOURCES.append
class CIA(RegexWikiAirport):
    airport_code = "CIA"
    page_name = "Carnoustie International Airport"
    regex = re.compile(
        r"\|\s*(?P<code>.*?)\s*\|\|\s*(?:\[\[(?P<airline>[^|]*?)]]|(?P<airline2>[^|]*?))\s*\|\|",
    )

@AIRPORT_SOURCES.append
class ERZ(RegexWikiAirport):
    airport_code = "ERZ"
    page_name = "Erzgard International Airport"
    regex = re.compile(
        r"\|-\n\|(?P<code>.*?)\n\|(?P<size>.).*?\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
    )

@AIRPORT_SOURCES.append
class ERZ2(RegexWikiAirport):
    airport_code = "ERZ"
    page_name = "Erzville Passenger Seaport"
    regex = re.compile(
        r"\|-\n\|(?P<code>S.*?)\n\|(?:\[\[(?P<airline>.*?)(?:\|[^]]*?|)]]|(?P<airline2>.+?)|)\n",
    )

    @staticmethod
    def size(_matches: dict[str, str]) -> str | None:
        return "SP"

@AIRPORT_SOURCES.append
class ATC(RegexWikiAirport):
    airport_code = "ATC"
    page_name = "Achowalogen Takachsin-Covina International Airport"
    regex = re.compile(
        r"\|-\n\|\s*(?P<code>[^|]*?)\s*\|\|[^|]*?\|\|\s*(?:\[\[(?P<airline>[^|]*?)(?:\|[^]]*?|)]][^|]*?|(?P<airline2>[^-|]*?)|-*?)\s*\|\|",
    )

@AIRPORT_SOURCES.append
class AIX(AirSource):
    name = "MRT Wiki (Airport AIX)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        cache = config.cache_dir / "aix"

        get_url(
            "https://docs.google.com/spreadsheets/d/1vG_oEj_XzZlckRwxn4jKkK1FcgjjaULpt66XcxClqP8/export?format=csv&gid=0",
            cache,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )

        self.df = pd.read_csv(cache, header=1)

    def build(self, config: Config):
        airport = self.airport(code="AIX", names={"Aurora International Airport"}, link=get_wiki_link("Aurora International Airport"))

        d = list(zip(self.df["Gate ID"], self.df["Gate Size"], self.df["Company"], strict=False))

        old_gate_size = None
        for gate_code, gate_size, airline in d:
            if str(gate_size) == "nan":
                gate_size = old_gate_size  # noqa: PLW2901
            else:
                gate_size = str(gate_size)[0]  # noqa: PLW2901
                old_gate_size = gate_size
            self.gate(code=gate_code, airport=airport, airline=self.airline(name=airline) if str(airline) != "nan" and airline != "Unavailable" else None, size=gate_size)


@AIRPORT_SOURCES.append
class LAR(AirSource):
    name = "MRT Wiki (Airport LAR)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        cache = config.cache_dir / "lar"

        get_url(
            "https://docs.google.com/spreadsheets/d/1TjGME8Hx_Fh5F0zgHBBvAj_Axlyk4bztUBELiEu4m-w/export?format=csv&gid=0",
            cache,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )

        self.df = pd.read_csv(cache)

    def build(self, config: Config):
        airport = self.airport(code="LAR", names={"Larkspur Lilyflower International Airport"}, link=get_wiki_link("Larkspur Lilyflower International Airport"))

        d = list(zip(self.df["Gate"], self.df["Size"], self.df["Airline"], self.df["Status"], strict=False))

        for gate_code, size, airline, _status in d:
            self.gate(code=gate_code, airport=airport, airline=self.airline(name=airline) if str(airline) != "nan" and airline != "?" else None, size=size)



@AIRPORT_SOURCES.append
class LFA(AirSource):
    name = "MRT Wiki (Airport LFA)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        cache = config.cache_dir / "lfa"

        get_url(
            "https://docs.google.com/spreadsheets/d/1TjGME8Hx_Fh5F0zgHBBvAj_Axlyk4bztUBELiEu4m-w/export?format=csv&gid=1289412824",
            cache,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )

        self.df = pd.read_csv(cache)

    def build(self, config: Config):
        airport = self.airport(code="LAR", names={"Larkspur Frankford Airfield"}, link=get_wiki_link("Larkspur Frankford Airfield"))

        d = list(zip(self.df["Gate"], self.df["Size"], self.df["Airline"], self.df["Status"], strict=False))

        for gate_code, size, airline, _status in d:
            self.gate(code=gate_code, airport=airport, airline=self.airline(name=airline) if str(airline) != "nan" and airline != "?" else None, size=size)
