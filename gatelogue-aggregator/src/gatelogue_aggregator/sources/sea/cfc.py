import difflib
import re
import uuid

import rich

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html, get_wiki_text
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop
from gatelogue_aggregator.types.source import Source


class CFC(SeaSource):
    name = "MRT Wiki (Sea, Caravacan Floaty Company)"
    priority = 1

    def __init__(self, config: Config):
        SeaSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = SeaCompany.new(self, name="Caravacan Floaty Company")
        stop_names = []

        text = get_wiki_text("Caravacan Floaty Company", config)
        for ln in text.split("\n"):
            if ". " not in ln:
                continue
            line_code, line_stations = ln.split(". ")
            if len(line_code) > 3:
                continue
            line = SeaLine.new(self, code=line_code, company=company, name=line_code, colour="#800")

            stops = []
            for stn in line_stations.split("--"):
                name = stn.strip(" '")
                stop_names.append(name)
                stop = SeaStop.new(self, codes={name}, name=name, company=company)
                stops.append(stop)

            if len(stops) == 0:
                continue

            SeaLineBuilder(self, line).connect(*stops)

            rich.print(RESULT + f"CFC Line {line_code} has {len(stops)} stops")

        ###

        names = []
        for warp in warps(uuid.UUID("7adc9642-5f67-4264-88e3-3c8bd93261c0"), config):
            if not warp["name"].startswith("CFC"):
                continue

            warp_name = warp["name"].split("_")[1]
            name = {
                ",": ",",
                "DeadbushW": "Deadbush Weezerville",
                "Leknes": "Leknes",
                "NSouthport": "New Southport",
                "NBakersville": "New Bakersville",
            }.get(warp_name, difflib.get_close_matches(warp_name, stop_names, 1, 0.0)[0])
            print(warp_name, name)
            if name in names:
                continue

            SeaStop.new(self, codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)

        self.save_to_cache(config, self.g)
