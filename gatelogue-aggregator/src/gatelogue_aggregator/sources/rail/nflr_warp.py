import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailSource
from gatelogue_aggregator.types.source import Source


class NFLRWarp(RailSource):
    name = "MRT Warp API (Rail, nFLR)"
    priority = 1

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="nFLR")

        codes = []
        for warp in warps(uuid.UUID("7e96f1a3-d9be-4ca8-a2ac-a67f49c6095e"), config):
            if not warp["name"].startswith("FLR") or warp["welcomeMessage"].startswith("Welcome"):
                continue
            code = warp["name"].split("-")[1].lower()
            if code in ("nsg", "rvb"):
                continue
            if code == "dne" and warp["name"].split("-")[2].lower() == "r5a":
                code = "dnw"
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
        self.save_to_cache(config, self.g)
