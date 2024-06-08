import re
import uuid
from pathlib import Path

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.sea import SeaContext, SeaSource


class IntraSailWarp(SeaSource):
    name = "MRT Warp API (Sea, IntraSail)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        SeaContext.__init__(self)
        Source.__init__(self)

        company = self.sea_company(name="IntraSail")

        names = []
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), cache_dir, timeout):
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
