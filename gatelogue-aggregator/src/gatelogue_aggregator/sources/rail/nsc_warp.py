import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class NSCWarp(RailSource):
    name = "MRT Warp API (Rail, Network South Central)"
    priority = 1

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="Network South Central")

        names = []
        for warp in warps(uuid.UUID("7e4855a9-0381-44bd-9a6d-165350410d80"), config):
            if warp["name"].startswith("NSC") and not warp["welcomeMessage"].startswith("Welcome"):
                continue
            if (match := re.search(r"(?i)^This is ([^.]*)\.", warp["welcomeMessage"])) is None:
                # rich.print(ERROR+"Unknown warp message format:", warp['welcomeMessage'])
                continue
            name = match.group(1)
            if name in names:
                continue
            self.rail_station(
                codes={name},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            names.append(name)
        self.save_to_cache(config, self.g)
