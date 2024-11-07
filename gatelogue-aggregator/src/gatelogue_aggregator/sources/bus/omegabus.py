import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.bus import BusContext, BusLineBuilder, BusSource


class IntraBusOmegaBus(BusSource):
    name = "MRT Wiki (Bus, IntraBus OmegaBus)"
    priority = 0

    def __init__(self, config: Config):
        BusContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.bus_company(name="IntraBus")

        html = get_wiki_html("OMEGAbus!", config)
        for table in html.find_all("table"):
            if "border-radius: 30px" not in table.attrs.get("style", ""):
                continue
            line_code = str(table("td")[0].find("span").string).strip()
            line = self.bus_line(code=line_code, company=company)

            stops = []
            for span in table("td")[1].find_all("span"):
                if span.find("s") is not None:
                    continue
                name = str(span.string).strip()
                stop = self.bus_stop(codes={name}, name=name, company=company)
                stops.append(stop)

            if len(stops) == 0:
                continue

            BusLineBuilder(self, line).connect(*stops)

            rich.print(RESULT + f"IntraBus OmegaBus Line {line_code} has {len(stops)} stops")
        self.save_to_cache(config, self.g)
