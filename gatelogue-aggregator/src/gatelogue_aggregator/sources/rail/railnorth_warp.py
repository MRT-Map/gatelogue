import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailSource,
    RailLineBuilder,
    RailSource,
    RailCompany,
    RailLine,
    RailStation,
)
from gatelogue_aggregator.types.source import Source


class RailNorthWarp(RailSource):
    name = "MRT Warp API (Rail, RailNorth)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="RailNorth")

        codes = []
        for warp in warps(uuid.UUID("f65bc7cb-ce43-477c-baf7-1b4c72798bd0"), config):
            if not warp["name"].startswith("RN"):
                continue
            code = warp["name"].split("-")[1].upper()
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
        self.save_to_cache(config, self.g)
