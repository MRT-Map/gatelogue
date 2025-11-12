import re

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)


class IntraRailLocal(RailSource):
    name = "MRT Wiki (Rail, IntraRail Local)"
    priority = 1

    def build(self, config: Config):
        company = RailCompany.new(self, name="IntraRail")

        for page in ("MCR Urban Scarborough", "MCR Urban Lumeva"):
            html = get_wiki_html(page, config)

            for table in html.find_all("table"):
                if "Code" not in table("th")[1].string:
                    continue
                span = table.previous_sibling.previous_sibling.find("span", class_="mw-headline")
                if (result := re.search(r"\((?P<code>.*?)\) (?P<name>.*)", span.string)) is None:
                    continue
                line_name = result.group("name")
                line_code = result.group("code") or line_name
                line = RailLine.new(self, code=line_code, name=line_name, company=company)

                stations = []
                for tr in table.find_all("tr"):
                    if len(tr("td")) != 4:
                        continue
                    name = tr("td")[2].string
                    station = RailStation.new(self, codes={name}, name=name, company=company)
                    stations.append(station)

                RailLineBuilder(self, line).connect(*stations)
