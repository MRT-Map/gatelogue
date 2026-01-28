from typing import TYPE_CHECKING

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import SeaSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html

if TYPE_CHECKING:
    import bs4


class IntraSail(SeaSource):
    name = "MRT Wiki (Sea, IntraSail)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("IntraSail", config)

    def build(self, config: Config):
        company = self.company(name="IntraSail")

        cursor: bs4.Tag = self.html.find("span", "mw-headline", string="1 Nansei Gintra").parent

        while cursor and (line_code_name := cursor.find(class_="mw-headline")) is not None:
            line_code, line_name = line_code_name.string.split(" ", 1)
            line_code = line_code.strip()
            line_name = line_name.strip()

            line_colour = "#C74EBD" if line_code.endswith("X") else "#3AB3DA" if line_code[-1].isdigit() else "#B02E26"
            line = self.line(code=line_code, name=line_name, company=company, mode="warp ferry", colour=line_colour)
            cursor: bs4.Tag = cursor.next_sibling.next_sibling.next_sibling.next_sibling

            builder = self.builder(line)
            for big in cursor.find_all("big"):
                if (big2 := big.find("big")) is None:
                    continue
                if (span := big.find("span")) is not None and span.attrs.get("style") in (
                    "color:#EA9D9B;",
                    "color:#AEE4ED;",
                ):
                    continue
                name = " ".join(big2.stripped_strings)

                builder.add(self.stop(codes={name}, name=name, company=company))

            if len(builder.station_list) == 0:
                continue
            builder.connect()

            cursor: bs4.Tag = cursor.next_sibling.next_sibling
