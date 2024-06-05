import itertools
import re
from pathlib import Path
from typing import TYPE_CHECKING

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.rail import Connection, RailContext, RailSource, Station

if TYPE_CHECKING:
    import bs4


class IntraRail(RailSource):
    name = "MRT Wiki (Rail, IntraRail)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.company(name="IntraRail")

        html = get_wiki_html("IntraRail", cache_dir, timeout)

        cursor: bs4.Tag = html.find("span", "mw-headline", string="(1) Whiteliner").parent

        while (line_code_name := cursor.find(class_="mw-headline").string).startswith("("):
            result = re.search(r"\((?P<code>.*)\) (?P<name>[^|]*)", line_code_name)
            line_code = result.group("code").strip()
            line_name = result.group("name").strip()
            line = self.line(code=line_code, name=line_name, company=company, mode="warp")
            cursor: bs4.Tag = cursor.next_sibling.next_sibling.next_sibling.next_sibling

            stations = []
            stations_dict = {}
            for big in cursor.find_all("big")[::2]:
                if big.find("s") is not None:
                    continue
                station_name = ""
                if (b := big.find("b")) is not None:
                    station_name += b.string
                if (i := big.find("i")) is not None:
                    station_name += " " + i.string
                if station_name == "":
                    continue
                station_name = station_name.strip()

                station = self.station(codes={station_name}, name=station_name, company=company)
                stations.append(station)
                stations_dict[station_name] = station

            if line_code == "54":
                for s1, s2 in itertools.pairwise(stations):
                    s1: Station
                    s2: Station
                    if s1.attrs(self).name in (
                        "Creeperville Shimoko",
                        "Shadowpoint Capitol Union Station",
                        "Shadowpoint Old Town",
                        "Shadowpoint South",
                    ):
                        s1.connect(self, s2, value=Connection(self, line=line))
                    if s1.attrs(self).name == "Creeperville Sakura Park":
                        s = stations_dict["New Cainport Riverside Stadium"]
                        s1.connect(self, s, value=Connection(self, line=line, one_way_towards=s.id))
                    if s1.attrs(self).name in (
                        "Creeperville Sakura Park",
                        "Winterside",
                        "Geneva Bay Hendon Road",
                    ):
                        s1.connect(self, s2, value=Connection(self, line=line, one_way_towards=s1.id))
                    if s1.attrs(self).name == "Hendon":
                        s = stations_dict["Geneva Bay New Indigo International Airport"]
                        s2.connect(self, s, value=Connection(self, line=line, one_way_towards=s.id))
                    if s1.attrs(self).name in ("New Cairnport Riverside Stadium", "Hendon"):
                        s1.connect(self, s2, value=Connection(self, line=line, one_way_towards=s2.id))
            else:
                for s1, s2 in itertools.pairwise(stations):
                    s1: Station
                    s2: Station
                    s1.connect(self, s2, value=Connection(self, line=line))

            if line_code == "66":
                line2 = self.line(code="<66>", name="East Mesan Express", company=company, mode="warp")
                stations2 = [
                    s
                    for s in stations
                    if s.attrs(self).name
                    not in (
                        "Aurora",
                        "Lazure",
                        "Cherrywood",
                        "Sunset Pass",
                        "Taiga Hills",
                        "Addison",
                        "Raymont",
                        "Bawktown South Station",
                    )
                ]
                for s1, s2 in itertools.pairwise(stations2):
                    s1: Station
                    s2: Station
                    s1.connect(self, s2, value=Connection(self, line=line2.id))
                rich.print(f"[green]  IntraRail Line <66> has {len(stations2)} stations")

            rich.print(f"[green]  IntraRail Line {line_code} has {len(stations)} stations")

            cursor: bs4.Tag = cursor.next_sibling.next_sibling
