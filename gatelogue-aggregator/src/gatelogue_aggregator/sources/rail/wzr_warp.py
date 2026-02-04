import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource


class WZRWarp(RailSource):
    name = "MRT Warp API (Rail, West Zeta Rail)"
    warps: list[dict]

    def prepare(self, config: Config):
        self.warps = list(warps(uuid.UUID("4230e859-a39b-4124-b368-28819b77f986"), config))

    def build(self, config: Config):
        company = self.company(name="West Zeta Rail")

        codes = []
        for warp in self.warps:
            if not warp["name"].startswith("WZR"):
                continue
            code = warp["name"].split("-")[-1]
            if code in codes:
                continue
            codes_ = {"PEA", "PBA"} if code == "PBA" else {code}
            self.station(codes=codes_, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            codes.append(code)
