from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.warp_api import WarpAPI


class WZRWarp(RailSource):
    name = "MRT Warp API (Rail, West Zeta Rail)"

    def build(self, config: Config):
        company = self.company(name="West Zeta Rail")

        codes = []
        for warp in WarpAPI.from_user("4230e859-a39b-4124-b368-28819b77f986"):
            if not warp.name.startswith("WZR"):
                continue
            code = warp.name.split("-")[-1]
            if code in codes:
                continue
            codes_ = {"PEA", "PBA"} if code == "PBA" else {code}
            self.station(codes=codes_, company=company, world="New", coordinates=warp.coordinates)
            codes.append(code)
