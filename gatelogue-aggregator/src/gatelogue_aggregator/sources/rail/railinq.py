import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource


class RaiLinQ(RailSource):
    name = "MRT Wiki (Rail, RaiLinQ)"
    priority = 0

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="RaiLinQ")

        html = get_wiki_html("List of RaiLinQ lines", config)
        for line_table in html.find_all("table"):
            if "border-radius: 11px" not in line_table.attrs.get("style", ""):
                continue
            line_code = str(line_table.find("th").find_all("span", style="color:white;")[0].b.string)
            line_name = str(line_table.find("th").find_all("span", style="color:white;")[1].i.string)
            line = self.rail_line(code=line_code, name=line_name, company=company, mode="warp")

            stations = []
            for b in line_table.p.find_all("b"):
                name = str(b.string)
                if name == "Wazamawazi Queen Maxima (Low Level)":
                    name = "Wazamawazi Queen Maxima"
                station = self.rail_station(codes={name}, name=name, company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"RaiLinQ Line {line_code} has {len(stations)} stations")
        self.save_to_cache(config, self.g)
