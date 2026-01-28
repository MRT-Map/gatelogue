import bs4

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import BusSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html


class IntraBus(BusSource):
    name = "MRT Wiki (Bus, IntraBus)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("IntraBus", config)

    def build(self, config: Config):
        company = self.company(name="IntraBus")

        for table in self.html.find_all("table"):
            if not table("th") or "Route Number" not in table.strings:
                continue
            shift = 1 if "Replacement For" in table.strings else 0
            for tr in table("tr")[1::2]:
                line_code = tr("td")[0].find("span").string
                line = self.line(code=line_code, company=company)

                builder = self.builder(line)
                for li in tr("td")[1 + shift]("li"):
                    if li.find("s") is not None:
                        continue
                    if (name := li.find("b")) is None:
                        continue
                    name = name.string
                    if (more := li.find("i")) is not None:
                        name += " " + more.string.strip()
                    builder.add(self.stop(codes={name}, name=name, company=company))

                if len(builder.station_list) == 0:
                    continue
                if line_code in ("313", "425"):
                    builder.connect_circle(one_way={"*": "forwards"})
                elif line_code == "419":
                    builder.connect(
                        one_way={
                            "Shenghua International Airport Terminal 1": "forwards",
                            "Shenghua International Airport Terminal 2": "forwards",
                        }
                    )
                    builder.connect_to("Shenghua Michigan Avenue", one_way="forwards")
                else:
                    builder.connect()
