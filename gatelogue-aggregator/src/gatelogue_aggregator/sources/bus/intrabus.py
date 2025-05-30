from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusLineBuilder, BusSource, BusStop


class IntraBus(BusSource):
    name = "MRT Wiki (Bus, IntraBus)"
    priority = 1

    def build(self, config: Config):
        company = BusCompany.new(self, name="IntraBus")

        html = get_wiki_html("IntraBus", config)
        for table in html.find_all("table"):
            if not table("th") or "Route Number" not in table.strings:
                continue
            shift = 1 if "Replacement For" in table.strings else 0
            for tr in table("tr")[1::2]:
                if tr("td")[3 + shift].find("a", href="/index.php/File:Rsz_open.png") is None:
                    continue
                line_code = tr("td")[0].find("span").string
                line = BusLine.new(self, code=line_code, company=company)

                stops = []
                for li in tr("td")[1 + shift]("li"):
                    name = li.find("b").string
                    if (more := li.find("i")) is not None:
                        name += " " + more.string.strip()
                    stop = BusStop.new(self, codes={name}, name=name, company=company)
                    stops.append(stop)

                if len(stops) == 0:
                    continue

                BusLineBuilder(self, line).connect(*stops)
