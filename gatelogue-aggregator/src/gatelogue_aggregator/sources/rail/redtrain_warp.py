from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.warp_api import WarpAPI


class RedTrainWarp(RailSource):
    name = "MRT Warp API (Rail, RedTrain)"

    def build(self, config: Config):
        company = self.company(name="RedTrain")

        codes = []
        for warp in WarpAPI.from_user("7dd701ed-5279-40d8-9db4-82ac57126c2c"):
            if not warp.name.startswith("RT"):
                continue
            code = warp.name.split("_")[1].upper()
            code = {"RITO": "ITO", "VEN": "VN", "MTH": "MSN", "WHT": "WH"}.get(code, code)
            if code in codes:
                continue
            self.station(
                codes={code},
                company=company,
                world="New",
                coordinates=warp.coordinates,
            )
            codes.append(code)
