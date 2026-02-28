import re

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.warp_api import WarpAPI


class NSCWarp(RailSource):
    name = "MRT Warp API (Rail, Network South Central)"
    warps: list[dict]

    def build(self, config: Config):
        company = self.company(name="Network South Central")

        names = []
        for warp in WarpAPI.from_user("7e4855a9-0381-44bd-9a6d-165350410d80"):
            if warp.name.startswith("NSC") and not warp.welcome_message.startswith("Welcome"):
                continue
            if (match := re.search(r"(?i)^This is ([^.]*)\.", warp.welcome_message)) is None:
                continue
            name = match.group(1)
            if name in names:
                continue
            self.station(
                codes={name},
                company=company,
                world="New",
                coordinates=warp.coordinates,
            )
            names.append(name)
