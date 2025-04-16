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


class SEAT(RailSource):
    name = "MRT Wiki (Rail, SEAT)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="SEAT")

        html = get_wiki_html("Seoland Economically/Ecologically Advanced Transit", config)
        first_seen = False
        for h3 in html.find_all("h3"):
            line_name: str = h3.find("span", class_="mw-headline").string
            if not first_seen:
                if "Savagebite" in line_name:
                    first_seen = True
                else:
                    continue

            line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp", colour="#000080")

            line_table = h3.find_next("table")
            if line_table is None or line_table.caption is None or "Line" not in line_table.caption.string:
                continue

            stations = []
            for tr in line_table("tr")[1:]:
                if "Open" not in next(tr("td")[3].strings):
                    continue
                name = tr("td")[1].string.strip().removesuffix(" Station")

                station = RailStation.new(self, codes={name}, name=name, company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            if line.name == "Cross Continental Line":
                RailLineBuilder(self, line).connect(*stations, between=(None, "Maple St."))
                RailLineBuilder(self, line).connect(*stations, between=("UCWTIA", None))
            else:
                RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"SEAT Line {line_name} has {len(stations)} stations")

        self.save_to_cache(config, self.g)
