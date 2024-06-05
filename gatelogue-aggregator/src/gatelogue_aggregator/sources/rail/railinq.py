import itertools
from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.rail import Connection, RailContext, RailSource, Station


class RaiLinQ(RailSource):
    name = "MRT Wiki (Rail, RaiLinQ)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.company(name="RaiLinQ")

        html = get_wiki_html("List of RaiLinQ lines", cache_dir, timeout)
        for line_table in html.find_all("table"):
            if "border-radius: 11px" not in line_table.attrs.get("style", ""):
                continue
            line_code = str(line_table.find("th").find_all("span", style="color:white;")[0].b.string)
            line_name = str(line_table.find("th").find_all("span", style="color:white;")[1].i.string)
            line = self.line(code=line_code, name=line_name, company=company, mode="warp")

            stations = []
            for b in line_table.p.find_all("b"):
                station = self.station(codes={str(b.string)}, name=str(b.string), company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            for s1, s2 in itertools.pairwise(stations):
                s1: Station
                s2: Station
                s1.connect(self, s2, value=Connection(line=line.id))

            rich.print(f"[green]  RaiLinQ Line {line_code} has {len(stations)} stations")
