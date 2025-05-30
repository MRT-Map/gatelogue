import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailSource,
    RailStation,
)


class MarbleRailWarp(RailSource):
    name = "MRT Warp API (Rail, MarbleRail)"
    priority = 0

    def build(self, config: Config):
        company = RailCompany.new(self, name="MarbleRail")

        codes = []
        for warp in warps(uuid.UUID("8d034d06-8332-479d-84f2-d3922400b1ed"), config):
            if (
                len(warp["name"].split("-")) > 1
                and not warp["name"].split("-")[1].startswith("MR")
                and warp["name"].split("-")[1] != "MTC"
            ):
                continue
            code = warp["name"].split("-")[0].upper()
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
