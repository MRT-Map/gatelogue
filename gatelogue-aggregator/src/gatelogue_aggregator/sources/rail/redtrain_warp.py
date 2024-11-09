import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailSource
from gatelogue_aggregator.types.source import Source


class RedTrainWarp(RailSource):
    name = "MRT Warp API (Rail, RedTrain)"
    priority = 1

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="RedTrain")

        codes = []
        for warp in warps(uuid.UUID("7dd701ed-5279-40d8-9db4-82ac57126c2c"), config):
            if not warp["name"].startswith("RT"):
                continue
            code = warp["name"].split("_")[1].upper()
            if code in codes:
                continue
            code = {"RITO": "ITO", "VEN": "VN", "MTH": "MSN"}.get(code, code)
            self.rail_station(
                codes={code},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            codes.append(code)
        self.save_to_cache(config, self.g)
