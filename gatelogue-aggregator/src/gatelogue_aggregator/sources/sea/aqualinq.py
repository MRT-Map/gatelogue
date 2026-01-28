import re
from typing import TYPE_CHECKING

from gatelogue_aggregator.source import SeaSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.config import Config

if TYPE_CHECKING:
    import bs4


class AquaLinQ(SeaSource):
    name = "MRT Wiki (Sea, AquaLinQ)"

    def build(self, config: Config):
        company = self.company(name="AquaLinQ")

        html = get_wiki_html("AquaLinQ", config)
        for h3 in html.find_all("h3"):
            if (match := re.search(r"([^:]*): (.*)", h3.find("span", class_="mw-headline").string)) is None:
                continue
            line_code = match.group(1)
            line_name = match.group(2)
            line = self.line(code=line_code, company=company, name=line_name, mode="warp ferry")

            p: bs4.Tag = h3.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling

            builder = self.builder(line)
            for b in (
                (a.strip() for a in p.strings if a.strip())
                if line_code == "AQ1800"
                else (b.string for b in p.find_all("b"))
            ):
                builder.add(self.stop(codes={b}, name=b, company=company))

            if len(builder.station_list) == 0:
                continue
            builder.connect()
