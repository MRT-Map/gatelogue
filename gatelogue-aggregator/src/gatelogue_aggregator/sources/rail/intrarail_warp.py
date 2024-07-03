import re
import uuid
from pathlib import Path

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class IntraRailWarp(RailSource):
    name = "MRT Warp API (Rail, IntraRail)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="IntraRail")

        names = []
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), cache_dir, timeout):
            if not warp["name"].startswith("IR"):
                continue
            if (
                match := re.search(
                    r"(?i)^This is ([^.]*)\.|THIS STOP: ([^/]*) /|THIS & LAST STOP: ([^/]*) /", warp["welcomeMessage"]
                )
            ) is None:
                # rich.print(ERROR+"Unknown warp message format:", warp['welcomeMessage'])
                continue
            name = match.group(1) or match.group(2) or match.group(3)
            name = {
                "Heampstead Kings Cross Railway Terminal": "Deadbush Heampstead Kings Cross Railway Terminal",
                "Musique": "Musique Bayview Avenue",
                "Zerez": "Zerez Thespe Railway Station",
                "Pine Mountain": "PMW City Pine Mountain",
                "Delta City": "Delta City Henry Avenue",
                "Matheson": "Matheson Araya Avenue",
                "Scarborough": "Scarborough MRT Plaza",
                "Cactus River": "Cactus River Main Street",
                "Southport": "Southfort",
                "Llanrwst Newydd": "Wurst",
                "Llanwrst Newydd": "Wurst",
            }.get(name, name)
            if name in names:
                continue
            self.rail_station(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
