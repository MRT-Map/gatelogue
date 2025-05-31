import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusLineBuilder, BusSource, BusStop


class IntraBusOmegaBus(BusSource):
    name = "MRT Wiki (Bus, IntraBus OmegaBus)"
    priority = 1

    def build(self, config: Config):
        company = BusCompany.new(self, name="IntraBus")

        html = get_wiki_html("OMEGAbus!", config)
        for table in html.find_all("table"):
            if "border-radius: 30px" not in table.attrs.get("style", ""):
                continue
            line_code = table("td")[0].find("span").string
            line = BusLine.new(self, code=line_code, company=company)

            stops = []
            for span in table("td")[1].find_all("span"):
                if span.find("s") is not None:
                    continue
                name = span.string
                stop = BusStop.new(self, codes={name}, name=name, company=company)
                stops.append(stop)

            if len(stops) == 0:
                continue

            BusLineBuilder(self, line).connect(*stops)

            
