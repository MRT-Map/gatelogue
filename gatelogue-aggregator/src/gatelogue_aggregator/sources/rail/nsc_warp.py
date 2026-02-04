import re
import uuid

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.source import RailSource


class NSCWarp(RailSource):
    name = "MRT Warp API (Rail, Network South Central)"
    warps: list[dict]

    def prepare(self, config: Config):
        self.warps = list(warps(uuid.UUID("7e4855a9-0381-44bd-9a6d-165350410d80"), config))

    def build(self, config: Config):
        company = self.company(name="Network South Central")

        names = []
        for warp in self.warps:
            if warp["name"].startswith("NSC") and not warp["welcomeMessage"].startswith("Welcome"):
                continue
            if (match := re.search(r"(?i)^This is ([^.]*)\.", warp["welcomeMessage"])) is None:
                continue
            name = match.group(1)
            if name in names:
                continue
            self.station(
                codes={name},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            names.append(name)
