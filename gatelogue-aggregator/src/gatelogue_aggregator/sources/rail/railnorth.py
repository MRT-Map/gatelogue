import bs4

from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.config import Config


class RailNorth(RailSource):
    name = "MRT Wiki (Rail, RailNorth)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("RailNorth", config)

    def build(self, config: Config):
        company = self.company(name="RailNorth")

        for table in self.html.find_all("table"):
            if "Code" not in table("th")[1].string:
                continue
            line_name = table.find_previous_sibling("h3").find("span", class_="mw-headline").string
            line = self.line(code=line_name, name=line_name, company=company, colour="#000080")

            builder = self.builder(line)
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:
                    continue
                if tr("td")[0].find("a", href="/index.php/File:Dynmap_Green_Flag.png") is None:
                    continue
                name = " ".join(tr("td")[2].strings).strip()
                code = next(tr("td")[1].strings)
                builder.add(self.station(codes={code}, name=name, company=company))

            builder.connect()
