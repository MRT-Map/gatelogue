import re

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.warp_api import WarpAPI


class IntraRailWarp(RailSource):
    name = "MRT Warp API (Rail, IntraRail)"

    def build(self, config: Config):
        company = self.company(name="IntraRail")

        names = [
            "Whiteley Southwold University",
            "Whiteley Southwold University Station",
            "Benion Town Center",
            "Schillerton Division Street Terminal",
            "Mons Pratus",
            "New Stone City South",
            "Zerez Thespe Railway Station",
        ]
        for warp in WarpAPI.from_user("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"):
            if not warp.name.startswith("ItR"):
                continue
            if warp.name == "ItR213-Anthro-SB":
                name = "Anthro Island City Hall"
            else:
                if (
                    match := re.search(
                        r"(?i)^This is ([^.]*)\.|(?:THIS|LAST) STOP: (.*?) //|THIS & LAST STOP: (.*?) //",
                        warp.welcome_message,
                    )
                ) is None:
                    continue
                name = match.group(1) or match.group(2) or match.group(3)
                name = {
                    "Miu Wan TTL Airport Terminal 1": "Miu Wan Tseng Tsz Leng International Airport Terminal 1",
                    "Miu Wan TTL Airport Terminal 2": "Miu Wan Tseng Tsz Leng International Airport Terminal 2",
                    "Upton Ulster Mesah Central Station": "Upton Ulster Mensah Central Station",
                    "Deadbush Blackwater": "Deadbush Blackwater / WMI",
                    "Murrville Arcadia International Airport": "Murrville-Arcadia International Airport",
                    "Achowalogen Takachsin Downtown Solarion": "Achowalogen Takachsin Orion",
                    "Achowalogen Takachsin Outer Solarion": "Achowalogen Takachsin Solarion",
                }.get(name, name)
            if name in names:
                continue
            self.station(codes={name}, company=company, name=name, world="New", coordinates=warp.coordinates)
            names.append(name)
