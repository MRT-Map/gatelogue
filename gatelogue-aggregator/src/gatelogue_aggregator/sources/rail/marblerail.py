from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)


class MarbleRail(RailSource):
    name = "MRT Wiki (Rail, MarbleRail)"
    priority = 1

    def build(self, config: Config):
        company = RailCompany.new(self, name="MarbleRail")

        html = get_wiki_html("MarbleRail", config)
        for line_table in html.find_all("table"):
            if line_table.caption is None:
                continue
            line_name = line_table.caption.string.strip()
            if line_name not in ("MarbleRail Main Line", "Erzville Line"):
                continue
            line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp", colour="#cc00cc")

            stations = []
            for tr in line_table.find_all("tr"):
                if len(tr("td")) != 5:  # noqa: PLR2004
                    continue
                if tr("td")[4].string.strip() != "Opened":
                    continue
                code = tr("td")[0].string
                name = tr("td")[1].string

                station = RailStation.new(self, codes={code}, name=name, company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            if line_name == "MarbleRail Main Line":
                RailLineBuilder(self, line).connect(*stations, between=(None, "Edwardsburg"))
                RailLineBuilder(self, line).connect(*stations, between=("Tung Wan", None))
            else:
                RailLineBuilder(self, line).connect(*stations)
