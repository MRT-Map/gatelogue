import re
from typing import TYPE_CHECKING

import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaContext, SeaLineBuilder, SeaSource
from gatelogue_aggregator.types.source import Source

if TYPE_CHECKING:
    import bs4


class AquaLinQ(SeaSource):
    name = "MRT Wiki (Sea, AquaLinQ)"
    priority = 0

    def __init__(self, config: Config):
        SeaContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.sea_company(name="AquaLinQ")

        html = get_wiki_html("AquaLinQ", config)
        for h3 in html.find_all("h3"):
            if (match := re.search(r"([^:]*): (.*)", h3.find("span", class_="mw-headline").string)) is None:
                continue
            line_code = match.group(1)
            line_name = match.group(2)
            line = self.sea_line(code=line_code, company=company, name=line_name, mode="ferry")

            p: bs4.Tag = h3.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling

            stops = []
            for b in p.find_all("b"):
                stop = self.sea_stop(codes={str(b.string)}, name=str(b.string), company=company)
                stops.append(stop)

            if len(stops) == 0:
                continue

            SeaLineBuilder(self, line).connect(*stops)

            rich.print(RESULT + f"AquaLinQ Line {line_code} has {len(stops)} stops")
        self.save_to_cache(config, self.g)
