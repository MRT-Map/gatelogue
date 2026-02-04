import bs4

from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.config import Config


class RaiLinQ(RailSource):
    name = "MRT Wiki (Rail, RaiLinQ)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("List of RaiLinQ lines", config)

    def build(self, config: Config):
        company = self.company(name="RaiLinQ")

        for line_table in self.html.find_all("table"):
            if "border-radius: 11px" not in line_table.attrs.get("style", ""):
                continue
            if line_table.find("th") is None:
                continue
            line_code = line_table.find("th").find_all("span", style="color:white;")[0].b.string
            if line_code in ("IC 0300", "ST 3100", "ST 2000"):
                continue
            line_name = line_table.find("th").find_all("span", style="color:white;")[1].i.string

            line_colour = "#ff5500" if line_code.startswith("IC") else "#ffaa00"
            line = self.line(code=line_code, name=line_name, company=company, mode="warp", colour=line_colour)

            builder = self.builder(line)
            for b in line_table.p.find_all("b"):
                name = str(b.string)
                if name == "Wazamawazi Queen Maxima (Low Level)":
                    name = "Wazamawazi Queen Maxima"
                builder.add(self.station(codes={name}, name=name, company=company))

            
            builder.connect()
