import difflib
import re
import uuid

import rich

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html, get_wiki_text
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailCompany, RailSource, RailLine, RailStation, RailLineBuilder
from gatelogue_aggregator.types.source import Source
from gatelogue_aggregator.utils import search_all


class SeabeastRail(RailSource):
    name = "MRT Wiki (Rail, Seabeast Rail)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="Seabeast Rail")
        line = RailLine.new(self, code="Green Line", company=company, name="Green Line", colour="green")
        stop_names = []

        text = get_wiki_text("Seabeast Rail", config)
        stops = []
        for match in search_all(
            re.compile(r"""\| style="background:green; border:none; " \|.*?
\| style ="border:none; " \| • ([^(\n]*)"""),
            text,
        ):
            name = match.group(1)
            stop_names.append(name)
            stop = RailStation.new(self, codes={name}, name=name, company=company)
            stops.append(stop)

        RailLineBuilder(self, line).connect(*stops)

        rich.print(RESULT + f"Seabeast Rail Green Line has {len(stops)} stops")

        ###

        names = []
        for warp in warps(uuid.UUID("99197ab5-4a78-4e99-b43b-fdf1e04ada1d"), config):
            if not warp["name"].startswith("SBR"):
                continue

            warp_name = warp["name"][6:]
            name = {}.get(
                warp_name,
                difflib.get_close_matches(warp_name, stop_names, 1, 0.0)[0],
            )
            if name in names:
                continue

            RailStation.new(self, codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)

        self.save_to_cache(config, self.g)
