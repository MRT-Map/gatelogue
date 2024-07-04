import re
from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource


class IntraRailLocal(RailSource):
    name = "MRT Wiki (Rail, IntraRail Local)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="IntraRail")

        for page in ("MCR Urban Scarborough", "MCR Urban Lumeva"):
            html = get_wiki_html(page, cache_dir, timeout)

            for table in html.find_all("table"):
                if "Code" not in table("th")[1].string:
                    continue
                span = table.previous_sibling.previous_sibling.find("span", class_="mw-headline")
                if (result := re.search(r"\((?P<code>.*?)\) (?P<name>.*)", span.string)) is None:
                    continue
                line_name = result.group("name")
                line_code = result.group("code") or line_name
                line = self.rail_line(code=str(line_code).strip(), name=str(line_name).strip(), company=company)

                stations = []
                for tr in table.find_all("tr"):
                    if len(tr("td")) != 4:  # noqa: PLR2004
                        continue
                    name = str(tr("td")[2].string).strip()
                    station = self.rail_station(codes={name}, name=name, company=company)
                    stations.append(station)

                RailLineBuilder(self, line).connect(*stations)

                rich.print(RESULT + f"IntraRail Local Line {line_code} has {len(stations)} stations")
