import bs4

from gatelogue_aggregator.source import BusSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.config import Config


class IntraBusOmegaBus(BusSource):
    name = "MRT Wiki (Bus, IntraBus OmegaBus)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("OMEGAbus!", config)

    def build(self, config: Config):
        company = self.company(name="IntraBus")

        for table in self.html.find_all("table"):
            if "border-radius: 30px" not in table.attrs.get("style", ""):
                continue
            line_code = table("td")[0].find("span").string
            line = self.line(code=line_code, company=company)

            builder = self.builder(line)
            for span in table("td")[1].find_all("span"):
                if span.find("s") is not None:
                    continue
                name = span.string
                builder.add(self.stop(codes={name}, name=name, company=company))

            if len(builder.station_list) == 0:
                continue
            builder.connect()
