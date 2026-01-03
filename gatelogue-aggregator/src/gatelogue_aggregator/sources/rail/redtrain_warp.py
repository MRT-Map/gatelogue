import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailSource,
    RailStation,
)


class RedTrainWarp(RailSource):
    name = "MRT Warp API (Rail, RedTrain)"
    priority = 0

    def build(self, config: Config):
        company = RailCompany.new(self, name="RedTrain")

        codes = []
        for warp in warps(uuid.UUID("7dd701ed-5279-40d8-9db4-82ac57126c2c"), config):
            if not warp["name"].startswith("RT"):
                continue
            code = warp["name"].split("_")[1].upper()
            code = {"RITO": "ITO", "VEN": "VN", "MTH": "MSN", "WHT": "WH"}.get(code, code)
            if code in codes:
                continue
            RailStation.new(
                self,
                codes={code},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            codes.append(code)
