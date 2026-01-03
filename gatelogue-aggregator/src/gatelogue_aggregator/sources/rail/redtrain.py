from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)


class RedTrain(RailSource):
    name = "MRT Wiki (Rail, RedTrain)"
    priority = 1

    def build(self, config: Config):
        company = RailCompany.new(self, name="RedTrain")

        html = get_wiki_html("RedTrain", config)

        for table in html.find_all("table"):
            if "Code" not in table("th")[1].string:
                continue
            line = RailLine.new(
                self, code="Time Zones High Speed", name="Time Zones High Speed", company=company, colour="#ff0000"
            )

            stations = []
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:
                    continue
                if tr("td")[0].find("a", href="/index.php/File:Dynmap_Green_Flag.png") is None:
                    continue
                name = " ".join(tr("td")[2].strings).strip().removesuffix(" £")
                code = next(tr("td")[1].strings)
                station = RailStation.new(self, codes={code}, name=name, company=company)
                stations.append(station)

            RailLineBuilder(self, line).connect(*stations)
