import re
import uuid
from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.logging import ERROR
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class WZRWarp(RailSource):
    name = "MRT Warp API (Rail, West Zeta Rail)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="West Zeta Rail")

        codes = []
        for warp in warps(uuid.UUID("4230e859-a39b-4124-b368-28819b77f986"), cache_dir, timeout):
            if not warp["name"].startswith("WZR"):
                continue
            code = warp["name"].split("-")[-1]
            if code in codes:
                continue
            self.station(codes={code}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            codes.append(code)
