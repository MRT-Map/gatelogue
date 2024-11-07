import re
from typing import TYPE_CHECKING

import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaContext, SeaLineBuilder, SeaSource

if TYPE_CHECKING:
    import bs4


class IntraSail(SeaSource):
    name = "MRT Wiki (Sea, IntraSail)"
    priority = 0

    def __init__(self, config: Config):
        SeaContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.sea_company(name="IntraSail")

        html = get_wiki_html("IntraSail", config)

        cursor: bs4.Tag = html.find("span", "mw-headline", string="[ 1 ] Nansei Gintra").parent

        while cursor and (line_code_name := cursor.find(class_="mw-headline").string).startswith("["):
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
                if stop_name == "New Southport Port of":
                    stop_name = "Port of New Southport"

                stop = self.sea_stop(codes={stop_name}, name=stop_name, company=company)
                stops.append(stop)

            SeaLineBuilder(self, line).connect(*stops)

            rich.print(RESULT + f"IntraSail Line {line_code} has {len(stops)} stops")

            cursor: bs4.Tag = cursor.next_sibling.next_sibling
        self.save_to_cache(config, self.g)
