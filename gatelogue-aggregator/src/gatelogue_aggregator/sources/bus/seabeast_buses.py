import difflib
import re
import uuid

import rich

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html, get_wiki_text
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.bus import BusCompany, BusSource, BusLine, BusStop, BusLineBuilder
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop
from gatelogue_aggregator.types.source import Source
from gatelogue_aggregator.utils import search_all


class SeabeastBuses(BusSource):
    name = "MRT Wiki (Bus, Seabeast Buses)"
    priority = 1

    def __init__(self, config: Config):
        BusSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = BusCompany.new(self, name="Seabeast Buses")
        stop_names = {}

        text = get_wiki_text("Seabeast Buses", config)
        for match in search_all(
            re.compile(r"""\|-
\| style="background:(?P<col>.*?);.*?
\|(?P<code>.*?)
\|(?P<origin>.*?)
\|.*?
\|(?P<dests>.*?)
\| style="background:green"""),
            text,
        ):
            line_code = match.group("code")
            line = BusLine.new(self, code=line_code, company=company, name=line_code, colour=match.group("col"))

            stops = []
            for name in (match.group("origin"), *match.group("dests").split(",")):
                name = name.strip()
                stop_names.setdefault(line_code, []).append(name)
                stop = BusStop.new(self, codes={name}, name=name, company=company)
                stops.append(stop)

            if len(stops) == 0:
                continue

            BusLineBuilder(self, line).connect(*stops)

            rich.print(RESULT + f"Seabeast Buses Line {line_code} has {len(stops)} stops")

        ###

        names = []
        for warp in warps(uuid.UUID("99197ab5-4a78-4e99-b43b-fdf1e04ada1d"), config):
            if not warp["name"].startswith("SBB"):
                continue

            warp_name = warp["name"][6:]
            name = {"HEN": "Hendon Coach Station"}.get(
                warp_name,
                next(iter(difflib.get_close_matches(warp_name, stop_names.get(warp["name"][3:6], []), 1, 0.0)), None),
            )
            print(name, warp_name, warp["name"])
            if name in names or name is None:
                continue

            BusStop.new(self, codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)

        self.save_to_cache(config, self.g)
