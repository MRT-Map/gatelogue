import re
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)

if TYPE_CHECKING:
    import bs4


class IntraRail(RailSource):
    name = "MRT Wiki (Rail, IntraRail)"
    priority = 1

    def build(self, config: Config):
        company = RailCompany.new(self, name="IntraRail")

        html = get_wiki_html("IntraRail", config)

        cursor: bs4.Tag = html.find("span", "mw-headline", string="(1) Whiteliner").parent

        while (line_code_name := cursor.find(class_="mw-headline").string).startswith("("):
            result = re.search(r"\((?P<code>.*)\) (?P<name>[^|]*)", line_code_name)
            line_code = result.group("code").strip()
            line_name = result.group("name").strip()
            line = RailLine.new(self, code=line_code, name=line_name, company=company, mode="warp")
            cursor: bs4.Tag = cursor.next_sibling.next_sibling.next_sibling.next_sibling

            stations = []
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
                if station_name == "Siletz Siletz Salvador":
                    station_name = "Siletz Salvador Station"

                station = RailStation.new(self, codes={station_name}, name=station_name, company=company)
                stations.append(station)

            if line_code == "54":
                forward_label = "towards " + stations[-1].names.v
                backward_label = "towards " + stations[0].names.v
                RailLineBuilder(self, line).connect(
                    *stations[0:2],
                    forward_direction=forward_label,
                    backward_direction=backward_label,
                )
                RailLineBuilder(self, line).connect(
                    *stations[8 - 1 : 12 - 1],
                    forward_direction=forward_label,
                    backward_direction=backward_label,
                )
                RailLineBuilder(self, line).connect(
                    stations[8 - 1], *stations[5 - 1 : 0 : -1], forward_direction=backward_label, one_way=True
                )
                RailLineBuilder(self, line).connect(
                    stations[1], *stations[6 - 1 : 9 - 1], forward_direction=forward_label, one_way=True
                )
            elif line_code == "55":
                RailLineBuilder(self, line).connect(*stations, one_way=True)
            else:
                RailLineBuilder(self, line).connect(*stations)

            if line_code == "66":
                line2 = RailLine.new(self, code="<66>", name="East Mesan Express", company=company, mode="warp")
                stations2 = [
                    s
                    for s in stations
                    if s.names
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
                RailLineBuilder(self, line2).connect(*stations2)

            cursor: bs4.Tag = cursor.next_sibling.next_sibling
