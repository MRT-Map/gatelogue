import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource
from gatelogue_aggregator.types.source import Source


class RedTrain(RailSource):
    name = "MRT Wiki (Rail, RedTrain)"
    priority = 0

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="RedTrain")

        html = get_wiki_html("RedTrain", config)

        for table in html.find_all("table"):
            if "Code" not in table("th")[1].string:
                continue
            line = self.rail_line(code="Time Zones High Speed", name="Time Zones High Speed", company=company)

            stations = []
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:  # noqa: PLR2004
                    continue
                if tr("td")[0].find("a", href="/index.php/File:Dynmap_Green_Flag.png") is None:
                    continue
                name = " ".join(tr("td")[2].strings).strip().removesuffix(" £")
                code = str(tr("td")[1].span.string).strip()
                station = self.rail_station(codes={code}, name=name, company=company)
                stations.append(station)

            RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"RedTrain has {len(stations)} stations")
        self.save_to_cache(config, self.g)
