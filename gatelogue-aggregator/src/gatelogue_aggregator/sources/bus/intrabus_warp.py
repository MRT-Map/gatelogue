import re

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import BusSource
from gatelogue_aggregator.sources.warp_api import WarpAPI


class IntraBusWarp(BusSource):
    name = "MRT Warp API (Rail, IntraBus)"

    def build(self, config: Config):
        company = self.company(name="IntraBus")

        names = []
        for warp in WarpAPI.from_user("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"):
            if not warp.name.startswith("IB"):
                continue
            if (
                match := re.search(
                    r"(?i)^This is ([^.]*)\.|(?:THIS|LAST) STOP: (.*?) //|THIS & LAST STOP: (.*?) //",
                    warp.welcome_message,
                )
            ) is None:
                continue

            name = (match.group(1) or match.group(2) or match.group(3)).split("(")[0].strip()
            name = {
                "Quris Markovi Theatre": "Quiris Markovi Theatre",
                "Southport-sur-mer": "Southport-sur-mer MCR Station",
                "Kwai Tin Airfield": "Kwai Tin Ha Shan Airport",
                "Mountain View Bus Terminal": "Mountain View",
                "Alexandriasburg Isle of Alexandria Port of Call": "Alexandriasburg Island of Alexandria Port of Call",
                "MRT Marina Large Ferries Dock": "MRT Marina Large Ferries Terminal",
                "Pamsterlin Town Hall": "Blackfriars Pamsterlin Town Hall",
                "Passlack Maggy Square": "Passlack Naggy Square",
                "Segville Grand Central Station": "Segville Grand Central",
            }.get(name, name)
            if name in names:
                continue
            self.stop(
                codes={name},
                company=company,
                world=warp.world,
                coordinates=warp.coordinates,
            )
            names.append(name)
