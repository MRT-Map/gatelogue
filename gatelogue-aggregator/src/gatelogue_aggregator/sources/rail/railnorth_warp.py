import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource


class RailNorthWarp(RailSource):
    name = "MRT Warp API (Rail, RailNorth)"
    warps: list[dict]

    def prepare(self, config: Config):
        self.warps = list(warps(uuid.UUID("f65bc7cb-ce43-477c-baf7-1b4c72798bd0"), config))

    def build(self, config: Config):
        company = self.company(name="RailNorth")

        codes = []
        for warp in self.warps:
            if not warp["name"].startswith("RN"):
                continue
            code = warp["name"].split("-")[1].upper()
            if code in codes:
                continue
            self.station(
                codes={code},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            codes.append(code)
