import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource


class MarbleRail(RailSource):
    name = "MRT Wiki (Rail, MarbleRail)"
    priority = 0

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="MarbleRail")

        html = get_wiki_html("MarbleRail", config)
        for line_table in html.find_all("table"):
            if line_table.caption is None:
                continue
            line_name = str(line_table.caption.string).strip()
            if line_name not in ("MarbleRail Main Line", "Erzville Line"):
                continue
            line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")

            stations = []
            for tr in line_table.find_all("tr"):
                if len(tr("td")) != 5:  # noqa: PLR2004
                    continue
                if tr("td")[4].string.strip() != "Opened":
                    continue
                code = str(tr("td")[0].string).strip()
                name = str(tr("td")[1].string).strip()

                station = self.rail_station(codes={code}, name=name, company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            if line_name == "MarbleRail Main Line":
                RailLineBuilder(self, line).connect(*stations[:-4])
                RailLineBuilder(self, line).connect(*stations[-4:])
            else:
                RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"MarbleRail {line_name} has {len(stations)} stations")
        self.save_to_cache(config, self.g)
