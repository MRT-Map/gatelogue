import re
from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.sea import SeaSource, SeaContext, SeaLineBuilder


class HBL(SeaSource):
    name = "MRT Wiki (Sea, Hummingbird Boat Lines)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        SeaContext.__init__(self)
        Source.__init__(self)

        company = self.sea_company(name="Hummingbird Boat Lines")

        html = get_wiki_html("Hummingbird Boat Lines", cache_dir, timeout)
        for td in html.find("table", class_="multicol").find_all("td"):
            for p, ul in zip(td.find_all("p"), td.find_all("ul"), strict=False):
                line_code = str(p.span.string or p.span.span.string).strip()
                line_name = str(p.b.string).strip()
                line_colour = re.match(r"background-color:\s*([^;]*)", p.span.attrs["style"]).group(1)
                line = self.sea_line(code=line_code, company=company, name=line_name, colour=line_colour)

                stops = []
                for li in ul.find_all("li"):
                    if "Planned" in li.strings:
                        continue
                    stop_name = "".join(li.strings)
                    stop = self.sea_stop(codes={stop_name}, name=stop_name, company=company)
                    stops.append(stop)

                if len(stops) == 0:
                    continue

                SeaLineBuilder(self, line).matrix(*stops)

                rich.print(RESULT + f"HBL Line {line_code} has {len(stops)} stops")
