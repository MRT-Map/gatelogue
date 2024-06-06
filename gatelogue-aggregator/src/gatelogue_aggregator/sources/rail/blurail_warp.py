import re
import uuid
from pathlib import Path

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.rail import RailSource, RailContext


class BluRailWarp(RailSource):
    name = "MRT Warp API (Rail, BluRail)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.company(name="BluRail")

        names = []
        for warp in warps(uuid.UUID("fe400b78-b441-4551-8ede-a1295434a13b"), cache_dir, timeout):
            if (not warp["name"].startswith("BLU")) or (
                match := re.match(r"(?i)^This is ([^.]*)\.|→ ([^|]*?) *\|", warp["welcomeMessage"])
            ) is None:
                continue
            name = match.group(1) or match.group(2)
            if name in names:
                continue
            self.station(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
