import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaContext, SeaSource
from gatelogue_aggregator.types.source import Source


class IntraSailWarp(SeaSource):
    name = "MRT Warp API (Sea, IntraSail)"
    priority = 1

    def __init__(self, config: Config):
        SeaContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.sea_company(name="IntraSail")

        names = []
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), config):
            if not warp["name"].startswith("IS"):
                continue
            if (
                match := re.search(
                    r"(?i)^Welcome to ([^,]*),|^THIS & LAST STOP: ([^/]*) /|THIS STOP: ([^/]*) /",
                    warp["welcomeMessage"],
                )
            ) is None:
                # rich.print(ERROR + "hUnknown warp message format:", warp['welcomeMessage'])
                continue
            name = match.group(1) or match.group(2) or match.group(3)
            if name in names:
                continue
            self.sea_stop(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
        self.save_to_cache(config, self.g)
