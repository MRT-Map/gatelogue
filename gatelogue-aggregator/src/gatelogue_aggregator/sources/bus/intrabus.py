from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.bus import BusContext, BusLineBuilder, BusSource


class IntraBus(BusSource):
    name = "MRT Wiki (Bus, IntraBus)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        BusContext.__init__(self)
        Source.__init__(self)

        company = self.bus_company(name="IntraBus")

        html1 = get_wiki_html("IntraBus", cache_dir, timeout)
        html2 = get_wiki_html("OMEGAbus!", cache_dir, timeout)
        for html in (html1, html2):
            for table in html.find_all("table"):
                if "border-radius: 30px" not in table.attrs.get("style", ""):
                    continue
                line_code = str(table("td")[0].find("span").string).strip()
                line = self.bus_line(code=line_code, company=company)

                stops = []
                for span in table("td")[1].find_all("span"):
                    if span.find("s") is not None:
                        continue
                    name = str(span.string).strip()
                    stop = self.bus_stop(codes={name}, name=name, company=company)
                    stops.append(stop)

                if len(stops) == 0:
                    continue

                BusLineBuilder(self, line).connect(*stops)

                rich.print(RESULT + f"IntraBus Line {line_code} has {len(stops)} stops")
