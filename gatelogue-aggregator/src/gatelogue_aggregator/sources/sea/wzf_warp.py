import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaContext, SeaSource
from gatelogue_aggregator.types.source import Source


class WZFWarp(SeaSource):
    name = "MRT Warp API (Sea, West Zeta Ferry)"
    priority = 1

    def __init__(self, config: Config):
        SeaContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.sea_company(name="West Zeta Ferry")

        codes = []
        for warp in warps(uuid.UUID("4230e859-a39b-4124-b368-28819b77f986"), config):
            if not warp["name"].startswith("WZF"):
                continue
            code = warp["name"].split("-")[-1]
            if code in codes:
                continue
            self.sea_stop(codes={code}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            codes.append(code)
        self.save_to_cache(config, self.g)
