import bs4

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html


class MarbleRail(RailSource):
    name = "MRT Wiki (Rail, MarbleRail)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("MarbleRail", config)

    def build(self, config: Config):
        company = self.company(name="MarbleRail")

        for line_table in self.html.find_all("table"):
            if line_table.caption is None:
                continue
            line_name = line_table.caption.string.split("(")[0].strip()
            if line_name not in ("Meridia Line",):
                continue
            line = self.line(code=line_name, name=line_name, company=company, mode="traincarts", colour="#cc00cc")

            builder = self.builder(line)
            for tr in line_table.find_all("tr"):
                if len(tr("td")) != 5:
                    continue
                if tr("td")[4].string.strip() != "Opened":
                    continue
                code = tr("td")[0].string
                name = tr("td")[1].string

                builder.add(self.station(codes={code}, name=name, company=company))

            builder.connect()
