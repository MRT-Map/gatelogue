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


class RaiLinQ(RailSource):
    name = "MRT Wiki (Rail, RaiLinQ)"
    priority = 1

    def build(self, config: Config):
        company = RailCompany.new(self, name="RaiLinQ")

        html = get_wiki_html("List of RaiLinQ lines", config)
        for line_table in html.find_all("table"):
            if "border-radius: 11px" not in line_table.attrs.get("style", ""):
                continue
            if line_table.find("th") is None:
                continue
            line_code = line_table.find("th").find_all("span", style="color:white;")[0].b.string
            line_name = line_table.find("th").find_all("span", style="color:white;")[1].i.string

            line_colour = "#ff5500" if line_code.startswith("IC") else "#ffaa00"
            line = RailLine.new(self, code=line_code, name=line_name, company=company, mode="warp", colour=line_colour)

            stations = []
            for b in line_table.p.find_all("b"):
                name = str(b.string)
                if name == "Wazamawazi Queen Maxima (Low Level)":
                    name = "Wazamawazi Queen Maxima"
                station = RailStation.new(self, codes={name}, name=name, company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"RaiLinQ Line {line_code} has {len(stations)} stations")
        
