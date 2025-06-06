import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailSource,
    RailStation,
)


class WZRWarp(RailSource):
    name = "MRT Warp API (Rail, West Zeta Rail)"
    priority = 0

    def build(self, config: Config):
        company = RailCompany.new(self, name="West Zeta Rail")

        codes = []
        for warp in warps(uuid.UUID("4230e859-a39b-4124-b368-28819b77f986"), config):
            if not warp["name"].startswith("WZR"):
                continue
            code = warp["name"].split("-")[-1]
            if code in codes:
                continue
            codes_ = {"PEA", "PBA"} if code == "PBA" else {code}
            RailStation.new(self, codes=codes_, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            codes.append(code)
