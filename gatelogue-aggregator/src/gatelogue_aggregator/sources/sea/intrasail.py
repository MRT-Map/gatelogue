import re
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop

if TYPE_CHECKING:
    import bs4


class IntraSail(SeaSource):
    name = "MRT Wiki (Sea, IntraSail)"
    priority = 1

    def build(self, config: Config):
        company = SeaCompany.new(self, name="IntraSail")

        html = get_wiki_html("IntraSail", config)

        cursor: bs4.Tag = html.find("span", "mw-headline", string="1 Nansei Gintra").parent

        while cursor and (line_code_name := cursor.find(class_="mw-headline").string) is not None:
            line_code, line_name = line_code_name.split(" ", 1)
            line_code = line_code.strip()
            line_name = line_name.strip()

            line_colour = "#C74EBD" if line_code.endswith("X") else "#3AB3DA" if line_code[-1].isdigit() else "#B02E26"
            line = SeaLine.new(self, code=line_code, name=line_name, company=company, mode="ferry", colour=line_colour)
            cursor: bs4.Tag = cursor.next_sibling.next_sibling.next_sibling.next_sibling

            stops = []
            for big in cursor.find_all("big"):
                if (big2 := big.find("big")) is None:
                    continue
                if (span := big.find("span")) is not None and span.attrs.get("style") in (
                    "color:#EA9D9B;",
                    "color:#AEE4ED;",
                ):
                    continue
                name = " ".join(big2.stripped_strings)

                stop = SeaStop.new(self, codes={name}, name=name, company=company)
                stops.append(stop)

            SeaLineBuilder(self, line).connect(*stops)

            cursor: bs4.Tag = cursor.next_sibling.next_sibling
