import re

import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaContext, SeaLineBuilder, SeaSource
from gatelogue_aggregator.types.source import Source


class HBL(SeaSource):
    name = "MRT Wiki (Sea, Hummingbird Boat Lines)"
    priority = 0

    def __init__(self, config: Config):
        SeaContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.sea_company(name="Hummingbird Boat Lines")

        html = get_wiki_html("Hummingbird Boat Lines", config)
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
        self.save_to_cache(config, self.g)
