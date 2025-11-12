import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailSource,
    RailStation,
)


class BreezeRailWarp(RailSource):
    name = "MRT Warp API (Rail, BreezeRail)"
    priority = 0

    def build(self, config: Config):
        company = RailCompany.new(self, name="BreezeRail")

        codes = []
        for warp in warps(uuid.UUID("07f82b2e-75d0-4fec-98c8-472cc1621e7d"), config):
            if len(warp["name"].split("_")) < 3 or not warp["name"].split("_")[0].startswith("BZ"):  # noqa: PLR2004
                continue
            code = warp["name"].split("_")[1].upper()
            if code in codes:
                continue
            RailStation.new(
                self,
                codes={code},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            codes.append(code)
