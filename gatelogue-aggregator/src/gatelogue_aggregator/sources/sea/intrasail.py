import re
from pathlib import Path
from typing import TYPE_CHECKING

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext
from gatelogue_aggregator.types.node.sea import SeaLineBuilder, SeaSource

if TYPE_CHECKING:
    import bs4


class IntraSail(SeaSource):
    name = "MRT Wiki (Rail, IntraSail)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.sea_company(name="IntraSail")

        html = get_wiki_html("IntraSail", cache_dir, timeout)

        cursor: bs4.Tag = html.find("span", "mw-headline", string="[ 1 ] Nansei Gintra").parent

        while (line_code_name := cursor.find(class_="mw-headline").string).startswith("["):
            result = re.search(r"\[ (?P<code>.*) ] (?P<name>[^|]*)", line_code_name)
            line_code = result.group("code").strip()
            line_name = result.group("name").strip()
            line = self.sea_line(code=line_code, name=line_name, company=company, mode="ferry")
            cursor: bs4.Tag = cursor.next_sibling.next_sibling.next_sibling.next_sibling

            stops = []
            for big in cursor.find_all("big"):
                if big.find("big") is not None:
                    continue
                stop_name = ""
                if (b := big.find("b")) is not None:
                    if b.parent.attrs.get("style") in ("color:#EA9D9B;", "color:#AEE4ED;"):
                        continue
                    stop_name += b.string or ""
                if (i := big.find("i")) is not None:
                    stop_name += " " + i.string or ""
                if stop_name == "" or stop_name.startswith("["):
                    continue
                stop_name = stop_name.strip()

                stop = self.sea_stop(codes={stop_name}, name=stop_name, company=company)
                stops.append(stop)

            SeaLineBuilder(self, line).connect(*stops)

            rich.print(RESULT + f"IntraSailRail Line {line_code} has {len(stops)} stops")

            cursor: bs4.Tag = cursor.next_sibling.next_sibling
