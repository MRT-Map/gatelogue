import re
from pathlib import Path

import bs4
import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.sea import SeaLineBuilder, SeaSource, SeaContext


class AquaLinQ(SeaSource):
    name = "MRT Wiki (Sea, AquaLinQ)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        SeaContext.__init__(self)
        Source.__init__(self)

        company = self.sea_company(name="AquaLinQ")

        html = get_wiki_html("AquaLinQ", cache_dir, timeout)
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

            rich.print(f"[green]  AquaLinQ Line {line_code} has {len(stops)} stops")
