import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource


class RedTrainWarp(RailSource):
    name = "MRT Warp API (Rail, RedTrain)"
    warps: list[dict]

    def prepare(self, config: Config):
        self.warps = list(warps(uuid.UUID("7dd701ed-5279-40d8-9db4-82ac57126c2c"), config))

    def build(self, config: Config):
        company = self.company(name="RedTrain")

        codes = []
        for warp in self.warps:
            if not warp["name"].startswith("RT"):
                continue
            code = warp["name"].split("_")[1].upper()
            code = {"RITO": "ITO", "VEN": "VN", "MTH": "MSN", "WHT": "WH"}.get(code, code)
            if code in codes:
                continue
            self.station(
                codes={code},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            codes.append(code)
