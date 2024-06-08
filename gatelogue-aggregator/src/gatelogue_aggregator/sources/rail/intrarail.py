import re
from pathlib import Path
from typing import TYPE_CHECKING

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource

if TYPE_CHECKING:
    import bs4


class IntraRail(RailSource):
    name = "MRT Wiki (Rail, IntraRail)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="IntraRail")

        html = get_wiki_html("IntraRail", cache_dir, timeout)

        cursor: bs4.Tag = html.find("span", "mw-headline", string="(1) Whiteliner").parent

        while (line_code_name := cursor.find(class_="mw-headline").string).startswith("("):
            result = re.search(r"\((?P<code>.*)\) (?P<name>[^|]*)", line_code_name)
            line_code = result.group("code").strip()
            line_name = result.group("name").strip()
            line = self.rail_line(code=line_code, name=line_name, company=company, mode="warp")
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

                station = self.rail_station(codes={station_name}, name=station_name, company=company)
                stations.append(station)

            if line_code == "54":
                forward_label = "towards " + stations[-1].merged_attr(self, "name").v
                backward_label = "towards " + stations[0].merged_attr(self, "name").v
                RailLineBuilder(self, line).connect(
                    *stations[0:2], forward_label=forward_label, backward_label=backward_label, one_way=True
                )
                RailLineBuilder(self, line).connect(
                    *stations[8:12], forward_label=forward_label, backward_label=backward_label, one_way=True
                )
                RailLineBuilder(self, line).connect(
                    stations[8], *stations[5:0:-1], forward_label=backward_label, one_way=True
                )
                RailLineBuilder(self, line).connect(
                    stations[1], *stations[6:9], forward_label=forward_label, one_way=True
                )
            else:
                RailLineBuilder(self, line).connect(*stations)

            if line_code == "66":
                line2 = self.rail_line(code="<66>", name="East Mesan Express", company=company, mode="warp")
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
                RailLineBuilder(self, line2).connect(*stations2)
                rich.print(RESULT + f"IntraRail Line <66> has {len(stations2)} stations")

            rich.print(RESULT + f"IntraRail Line {line_code} has {len(stations)} stations")

            cursor: bs4.Tag = cursor.next_sibling.next_sibling
