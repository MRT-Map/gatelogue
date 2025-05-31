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


class NSCWarp(RailSource):
    name = "MRT Warp API (Rail, Network South Central)"
    priority = 0

    def build(self, config: Config):
        company = RailCompany.new(self, name="Network South Central")

        names = []
        for warp in warps(uuid.UUID("7e4855a9-0381-44bd-9a6d-165350410d80"), config):
            if warp["name"].startswith("NSC") and not warp["welcomeMessage"].startswith("Welcome"):
                continue
            if (match := re.search(r"(?i)^This is ([^.]*)\.", warp["welcomeMessage"])) is None:
                continue
            name = match.group(1)
            if name in names:
                continue
            RailStation.new(
                self,
                codes={name},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            names.append(name)
        
