import uuid

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.source import RailSource


class BreezeRailWarp(RailSource):
    name = "MRT Warp API (Rail, BreezeRail)"
    warps: list[dict]

    def prepare(self, config: Config):
        self.warps = list(warps(uuid.UUID("07f82b2e-75d0-4fec-98c8-472cc1621e7d"), config))

    def build(self, config: Config):
        company = self.company(name="BreezeRail")

        codes = []
        for warp in self.warps:
            if len(warp["name"].split("_")) < 3 or not warp["name"].split("_")[0].startswith("BZ"):
                continue
            code = warp["name"].split("_")[1].upper()
            if code in codes:
                continue
            self.station(
                codes={code},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            codes.append(code)
