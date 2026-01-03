import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.bus import BusCompany, BusSource, BusStop


class IntraBusWarp(BusSource):
    name = "MRT Warp API (Rail, IntraBus)"
    priority = 0

    def build(self, config: Config):
        company = BusCompany.new(self, name="IntraBus")

        names = []
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), config):
            if not warp["name"].startswith("IB"):
                continue
            if (
                match := re.search(
                    r"(?i)^This is ([^.]*)\.|(?:THIS|LAST) STOP: (.*?) //|THIS & LAST STOP: (.*?) //",
                    warp["welcomeMessage"],
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
            BusStop.new(
                self,
                codes={name},
                company=company,
                world="New" if warp["worldUUID"] == "253ced62-9637-4f7b-a32d-4e3e8e767bd1" else "Old",
                coordinates=(warp["x"], warp["z"]),
            )
            names.append(name)
