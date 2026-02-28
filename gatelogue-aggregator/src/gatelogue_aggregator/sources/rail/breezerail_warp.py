from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.warp_api import WarpAPI


class BreezeRailWarp(RailSource):
    name = "MRT Warp API (Rail, BreezeRail)"

    def build(self, config: Config):
        company = self.company(name="BreezeRail")

        codes = []
        for warp in WarpAPI.from_user("07f82b2e-75d0-4fec-98c8-472cc1621e7d"):
            if len(warp.name.split("_")) < 3 or not warp.name.split("_")[0].startswith("BZ"):
                continue
            code = warp.name.split("_")[1].upper()
            if code in codes:
                continue
            self.station(
                codes={code},
                company=company,
                world="New",
                coordinates=warp.coordinates,
            )
            codes.append(code)
