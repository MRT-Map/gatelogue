import re
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop

if TYPE_CHECKING:
    import bs4


class AquaLinQ(SeaSource):
    name = "MRT Wiki (Sea, AquaLinQ)"
    priority = 1

    def build(self, config: Config):
        company = SeaCompany.new(self, name="AquaLinQ")

        html = get_wiki_html("AquaLinQ", config)
        for h3 in html.find_all("h3"):
            if (match := re.search(r"([^:]*): (.*)", h3.find("span", class_="mw-headline").string)) is None:
                continue
            line_code = match.group(1)
            line_name = match.group(2)
            line = SeaLine.new(self, code=line_code, company=company, name=line_name, mode="ferry")

            p: bs4.Tag = h3.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling

            stops = []
            for b in (
                (a.strip() for a in p.strings if a.strip())
                if line_code == "AQ1800"
                else (b.string for b in p.find_all("b"))
            ):
                stop = SeaStop.new(self, codes={b}, name=b, company=company)
                stops.append(stop)

            if len(stops) == 0:
                continue

            SeaLineBuilder(self, line).connect(*stops)
