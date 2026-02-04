import bs4

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html


class SEAT(RailSource):
    name = "MRT Wiki (Rail, SEAT)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("Seoland Economically/Ecologically Advanced Transit", config)

    def build(self, config: Config):
        company = self.company(name="SEAT")

        first_seen = False
        for h3 in self.html.find_all("h3"):
            line_name: str = h3.find("span", class_="mw-headline").string
            if not first_seen:
                if "Savagebite" in line_name:
                    first_seen = True
                else:
                    continue

            line = self.line(code=line_name, name=line_name, company=company, mode="warp", colour="#000080")

            line_table = h3.find_next("table")
            if line_table is None or line_table.caption is None or "Line" not in line_table.caption.string:
                continue

            builder = self.builder(line)
            for tr in line_table("tr")[1:]:
                if all("Open" not in a for a in tr("td")[3].strings):
                    continue
                name = tr("td")[1].string.strip().removesuffix(" Station")

                builder.add(self.station(codes={name}, name=name, company=company))

            if line.name == "Cross Continental Line":
                builder.connect(until="Maple St.")
                builder.skip(until="UCWTIA", detached=True)
                builder.connect()
            else:
                builder.connect()
