import re
import uuid
from pathlib import Path

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class BluRailWarp(RailSource):
    name = "MRT Warp API (Rail, BluRail)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="BluRail")

        names = []
        for warp in warps(uuid.UUID("fe400b78-b441-4551-8ede-a1295434a13b"), cache_dir, timeout):
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
            elif code == "MCN" and match.group(1) == "11":
                code += "11"
            elif code == "STE" and match.group(1) == "1":
                code += "1"
            self.rail_station(codes={code}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
