import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.source import Source


class RailNorth(RailSource):
    name = "MRT Wiki (Rail, RailNorth)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="RailNorth")

        html = get_wiki_html("RailNorth", config)

        for table in html.find_all("table"):
            if "Code" not in table("th")[1].string:
                continue
            line_name = table.find_previous_sibling("h3").find("span", class_="mw-headline").string
            line = RailLine.new(self, code=line_name, name=line_name, company=company, colour="#000080")

            stations = []
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:  # noqa: PLR2004
                    continue
                if tr("td")[0].find("a", href="/index.php/File:Dynmap_Green_Flag.png") is None:
                    continue
                name = " ".join(tr("td")[2].strings).strip()
                code = tr("td")[1].string
                station = RailStation.new(self, codes={code}, name=name, company=company)
                stations.append(station)

            RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"{line_name} has {len(stations)} stations")
        self.save_to_cache(config, self.g)
