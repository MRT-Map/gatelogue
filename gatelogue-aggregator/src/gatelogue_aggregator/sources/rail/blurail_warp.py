import re
import uuid

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.source import RailSource


class BluRailWarp(RailSource):
    name = "MRT Warp API (Rail, BluRail)"
    warps: list[dict]

    def prepare(self, config: Config):
        self.warps = list(warps(uuid.UUID("fe400b78-b441-4551-8ede-a1295434a13b"), config))

    def build(self, config: Config):
        company = self.company(name="BluRail")

        names = [
            "Sunshine Coast Docks",
            "Cornwall",
            "South Paixton",
            "Seoland North",
            "Titsensaki BluRail Station",
            "Titsensaki",
            "Titsensaki Transfer",
        ]
        for warp in self.warps:
            if not warp["name"].startswith("BLU") and not warp["name"].startswith("BR"):
                continue
            if (match := re.search(r"(?i)^This is ([^.]*)\.|^[→✈] ([^|]*?) *\|", warp["welcomeMessage"])) is None:
                continue

            name = match.group(1) or match.group(2)
            if name in names:
                continue
            if (match := re.search(r"(\d*)_(...)_", warp["name"])) is None:
                continue

            code = {
                "Rosslyn": "RLN",
                "Murrville Central": "MUR",
                "Zaquar Tanzanite Station": "ZQT",
                "Spruce Neck": "FDR",
                "Chalxior Femtoprism Airfield": "CFA",
                "Ilirea Transit Center": "ITC",
                "Elecna Bay North": "EBN",
                "Utopia - IKEA": "UIK",
                "Seoland Powell Street": "SPS",
                "Titsensaki Palm Shores": "TPS",
                "Washingcube Airfield": "WCA",
            }.get(name, match.group(2))
            self.station(codes={code}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
