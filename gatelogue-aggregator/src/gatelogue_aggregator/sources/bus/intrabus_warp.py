import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.bus import BusCompany, BusSource, BusStop
from gatelogue_aggregator.types.node.sea import SeaSource
from gatelogue_aggregator.types.source import Source


class IntraBusWarp(BusSource):
    name = "MRT Warp API (Rail, IntraBus)"
    priority = 1

    def __init__(self, config: Config):
        SeaSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = BusCompany.new(self, name="IntraBus")

        names = []
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), config):
            if not warp["name"].startswith("IB"):
                continue
            if (
                match := re.search(
                    r"(?i)^This is ([^.]*)\.|THIS STOP: ([^/]*) /|THIS & LAST STOP: ([^/]*) /", warp["welcomeMessage"]
                )
            ) is None:
                # rich.print(ERROR+"Unknown warp message format:", warp['welcomeMessage'])
                continue
            name = match.group(1) or match.group(2) or match.group(3)
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
        self.save_to_cache(config, self.g)
