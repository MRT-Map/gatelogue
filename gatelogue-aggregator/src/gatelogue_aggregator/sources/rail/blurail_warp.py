import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class BluRailWarp(RailSource):
    name = "MRT Warp API (Rail, BluRail)"
    priority = 1

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="BluRail")

        names = []
        for warp in warps(uuid.UUID("fe400b78-b441-4551-8ede-a1295434a13b"), config):
            if not warp["name"].startswith("BLU") and not warp["name"].startswith("BR"):
                continue
            if (match := re.search(r"(?i)^This is ([^.]*)\.|^→ ([^|]*?) *\|", warp["welcomeMessage"])) is None:
                # rich.print(ERROR+"Unknown warp message format:", warp['welcomeMessage'])
                continue

            name = match.group(1) or match.group(2)
            if name in names:
                continue
            if (match := re.search(r"(\d*)_(...)_", warp["name"])) is None:
                continue

            code = match.group(2)
            if code == "BCH":
                code += match.group(1)
            elif code == "MCN" and (match.group(1) == "11" or match.group(1) == "6"):
                code += "11"
            elif code == "STE" and match.group(1) == "1":
                code += "1"
            self.rail_station(codes={code}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
        self.save_to_cache(config, self.g)
