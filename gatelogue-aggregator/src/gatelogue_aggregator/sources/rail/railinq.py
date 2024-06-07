from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import INFO2, RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource


class RaiLinQ(RailSource):
    name = "MRT Wiki (Rail, RaiLinQ)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="RaiLinQ")

        html = get_wiki_html("List of RaiLinQ lines", cache_dir, timeout)
        for line_table in html.find_all("table"):
            if "border-radius: 11px" not in line_table.attrs.get("style", ""):
                continue
            line_code = str(line_table.find("th").find_all("span", style="color:white;")[0].b.string)
            line_name = str(line_table.find("th").find_all("span", style="color:white;")[1].i.string)
            line = self.rail_line(code=line_code, name=line_name, company=company, mode="warp")

            stations = []
            for b in line_table.p.find_all("b"):
                station = self.station(codes={str(b.string)}, name=str(b.string), company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"RaiLinQ Line {line_code} has {len(stations)} stations")
