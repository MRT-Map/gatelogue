import re
import uuid
from pathlib import Path

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.rail import RailContext, RailSource


class IntraRailWarp(RailSource):
    name = "MRT Warp API (Rail, IntraRail)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.company(name="IntraRail")

        names = []
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), cache_dir, timeout):
            if (not warp["name"].startswith("IR")) or (
                match := re.match(r"(?i)^This is ([^.]*)\.", warp["welcomeMessage"])
            ) is None:
                continue
            name = match.group(1)
            if name in names:
                continue
            self.station(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
