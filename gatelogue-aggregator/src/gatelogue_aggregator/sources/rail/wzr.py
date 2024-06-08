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


class WZR(RailSource):
    name = "MRT Wiki (Rail, West Zeta Rail)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="West Zeta Rail")

        html = get_wiki_html("West Zeta Rail", cache_dir, timeout)

        for table in html.find_all("table"):
            if "Code" not in table.th.string:
                continue
            span = table.previous_sibling.previous_sibling.find(
                "span", class_="mw-headline"
            ) or table.previous_sibling.previous_sibling.previous_sibling.previous_sibling.find(
                "span", class_="mw-headline"
            )
            if (result := re.search(r"Line (?P<code>.*?) - (?P<name>.*)|(?P<name2>[^(]*)", span.string)) is None:
                continue
            line_name = result.group("name") or result.group("name2")
            line_code = result.group("code") or line_name
            line = self.rail_line(code=str(line_code).strip(), name=str(line_name).strip(), company=company)

            stations = []
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:
                    continue
                if tr("td")[3].string.strip() == "Planned":
                    continue
                code = str(tr("td")[0].string).strip()
                name = "".join(tr("td")[1].strings).strip().rstrip("*")
                print(code, name)
                station = self.station(codes={code}, name=name, company=company)
                stations.append(station)

            RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"WZR Line {line_code} has {len(stations)} stations")
