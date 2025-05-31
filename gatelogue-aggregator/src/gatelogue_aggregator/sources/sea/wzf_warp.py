import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaSource, SeaStop
from gatelogue_aggregator.types.source import Source


class WZFWarp(SeaSource):
    name = "MRT Warp API (Sea, West Zeta Ferry)"
    priority = 0

    def build(self, config: Config):
        company = SeaCompany.new(self, name="West Zeta Ferry")

        codes = []
        for warp in warps(uuid.UUID("4230e859-a39b-4124-b368-28819b77f986"), config):
            if not warp["name"].startswith("WZF") and not warp["name"].startswith("ZF"):
                continue
            code = warp["name"].split("-")[-1]
            if code in codes:
                continue
            SeaStop.new(self, codes={code}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            codes.append(code)
        
