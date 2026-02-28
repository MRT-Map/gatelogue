from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import SeaSource
from gatelogue_aggregator.sources.warp_api import WarpAPI


class WZFWarp(SeaSource):
    name = "MRT Warp API (Sea, West Zeta Ferry)"

    def build(self, config: Config):
        company = self.company(name="West Zeta Ferry")

        codes = []
        for warp in WarpAPI.from_user("4230e859-a39b-4124-b368-28819b77f986"):
            if not warp.name.startswith("WZF") and not warp.name.startswith("ZF"):
                continue
            code = warp.name.split("-")[-1]
            code = {"PBA": "PEA"}.get(code, code)
            if code in codes:
                continue
            self.stop(codes={code}, company=company, world="New", coordinates=warp.coordinates)
            codes.append(code)
