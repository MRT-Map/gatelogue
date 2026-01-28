import itertools
import re

import bs4

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import SeaSource


class HBL(SeaSource):
    name = "MRT Wiki (Sea, Hummingbird Boat Lines)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("Hummingbird Boat Lines", config)

    def build(self, config: Config):
        company = self.company(name="Hummingbird Boat Lines")


        for td in self.html.find("table", class_="multicol").find_all("td"):
            for p, ul in zip(td.find_all("p"), td.find_all("ul"), strict=False):
                line_code = p.span.string or p.span.span.string
                line_name = p.b.string
                line_colour = re.match(r"background-color:\s*([^;]*)", p.span.attrs["style"]).group(1)
                line = self.line(code=line_code, company=company, name=line_name, colour=line_colour, mode="warp ferry")

                docks = []
                for li in ul.find_all("li"):
                    if "Planned" in li.strings:
                        continue
                    stop_name = "".join(li.strings)
                    stop = self.stop(codes={stop_name}, name=stop_name, company=company)
                    docks.append(self.dock(code=line.code, stop=stop))

                if len(docks) == 0:
                    continue
                for d1, d2 in itertools.permutations(docks, 2):
                    self.connection(line=line, from_=d1, to=d2)
