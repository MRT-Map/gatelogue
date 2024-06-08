import re
import uuid
from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.logging import ERROR
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.bus import BusSource
from gatelogue_aggregator.types.node.rail import RailContext, RailSource
from gatelogue_aggregator.types.node.sea import SeaContext, SeaSource


class IntraBusWarp(BusSource):
    name = "MRT Warp API (Rail, IntraBus)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        SeaContext.__init__(self)
        Source.__init__(self)

        company = self.bus_company(name="IntraBus")

        names = []
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), cache_dir, timeout):
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
            self.bus_stop(
                codes={name},
                company=company,
                world="New" if warp["worldUUID"] == "253ced62-9637-4f7b-a32d-4e3e8e767bd1" else "Old",
                coordinates=(warp["x"], warp["z"]),
            )
            names.append(name)
