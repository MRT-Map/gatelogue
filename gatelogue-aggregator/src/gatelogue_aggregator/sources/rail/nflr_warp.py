import uuid
from pathlib import Path

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class NFLRWarp(RailSource):
    name = "MRT Warp API (Rail, nFLR)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="nFLR")

        codes = []
        for warp in warps(uuid.UUID("7e96f1a3-d9be-4ca8-a2ac-a67f49c6095e"), cache_dir, timeout):
            if not warp["name"].startswith("FLR") or warp["welcomeMessage"].startswith("Welcome"):
                continue
            code = warp["name"].split("-")[1].lower()
            if code in ("nsg", "rvb"):
                continue
            code = {
                "n104": {"n104", "n203", "n300"},
                "n203": {"n104", "n203", "n300"},
                "n300": {"n104", "n203", "n300"},
                "hzc": {"hzc", "n213"},
                "n213": {"hzc", "n213"},
                "frg": {"frg", "n214"},
                "n214": {"frg", "n214"},
            }.get(code, {code})
            if code in codes:
                continue
            self.rail_station(
                codes=code,
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
                name=warp["welcomeMessage"].split("|")[0].strip(),
            )
            codes.append(code)
