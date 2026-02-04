import bs4

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html


class RedTrain(RailSource):
    name = "MRT Wiki (Rail, RedTrain)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("RedTrain", config)

    def build(self, config: Config):
        company = self.company(name="RedTrain")

        for table in self.html.find_all("table"):
            if "Code" not in table("th")[1].string:
                continue
            line = self.line(
                code="Time Zones High Speed", name="Time Zones High Speed", company=company, colour="#ff0000"
            )

            builder = self.builder(line)
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:
                    continue
                if tr("td")[0].find("a", href="/index.php/File:Dynmap_Green_Flag.png") is None:
                    continue
                name = " ".join(tr("td")[2].strings).strip().removesuffix(" £")
                code = next(tr("td")[1].strings)
                builder.add(self.station(codes={code}, name=name, company=company))

            builder.connect()
