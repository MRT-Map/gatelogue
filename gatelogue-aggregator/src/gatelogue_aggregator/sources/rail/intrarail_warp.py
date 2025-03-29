import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.source import Source


class IntraRailWarp(RailSource):
    name = "MRT Warp API (Rail, IntraRail)"
    priority = 0

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="IntraRail")

        names = [
            "Whiteley Southwold University",
            "Whiteley Southwold University Station",
            "Benion Town Center",
            "Schillerton Division Street Terminal",
            "Mons Pratus",
            "New Stone City South",
            "Zerez Thespe Railway Station",
        ]
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), config):
            if not warp["name"].startswith("ItR"):
                continue
            if (
                match := re.search(
                    r"(?i)^This is ([^.]*)\.|(?:THIS|LAST) STOP: (.*?) //|THIS & LAST STOP: (.*?) //",
                    warp["welcomeMessage"],
                )
            ) is None:
                # rich.print(ERROR+"Unknown warp message format:", warp['welcomeMessage'])
                continue
            name = match.group(1) or match.group(2) or match.group(3)
            name = {
                "Miu Wan TTL Airport Terminal 1": "Miu Wan Tseng Tsz Leng International Airport Terminal 1",
                "Miu Wan TTL Airport Terminal 2": "Miu Wan Tseng Tsz Leng International Airport Terminal 2",
                "Upton Ulster Mesah Central Station": "Upton Ulster Mensah Central Station",
                "Deadbush Blackwater": "Deadbush Blackwater / WMI",
                "Murrville Arcadia International Airport": "Murrville-Arcadia International Airport",
                "Fortaleza": "Fortaleza Marina",
            }.get(name, name)
            if name in names:
                continue
            RailStation.new(
                self, codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"])
            )
            names.append(name)
        self.save_to_cache(config, self.g)
