import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.bus import BusContext, BusLineBuilder, BusSource
from gatelogue_aggregator.types.source import Source


class IntraBus(BusSource):
    name = "MRT Wiki (Bus, IntraBus)"
    priority = 0

    def __init__(self, config: Config):
        BusContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.bus_company(name="IntraBus")

        html = get_wiki_html("IntraBus", config)
        for table in html.find_all("table"):
            if not table("th") or "Route Number" not in table.strings:
                continue
            shift = 1 if "Replacement For" in table.strings else 0
            for tr in table("tr")[1::2]:
                if tr("td")[3 + shift].find("a", href="/index.php/File:Rsz_open.png") is None:
                    continue
                line_code = str(tr("td")[0].find("span").string).strip()
                line = self.bus_line(code=line_code, company=company)

                stops = []
                for li in tr("td")[1 + shift]("li"):
                    name = str(li.find("b").string).strip()
                    if (more := li.find("i")) is not None:
                        name += " " + more.string.strip()
                    stop = self.bus_stop(codes={name}, name=name, company=company)
                    stops.append(stop)

                if len(stops) == 0:
                    continue

                BusLineBuilder(self, line).connect(*stops)

                rich.print(RESULT + f"IntraBus Line {line_code} has {len(stops)} stops")

        self.save_to_cache(config, self.g)
