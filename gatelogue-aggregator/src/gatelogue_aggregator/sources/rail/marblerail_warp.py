import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class MarbleRailWarp(RailSource):
    name = "MRT Warp API (Rail, MarbleRail)"
    priority = 1

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="MarbleRail")

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
            self.rail_station(
                codes={code},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            codes.append(code)
        self.save_to_cache(config, self.g)
