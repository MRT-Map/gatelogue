from pathlib import Path

import msgspec

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.types.air import AirContext
from gatelogue_aggregator.types.base import Source, Sourced


class DynmapAirports(AirContext, Source):
    name = "MRT Dynmap"

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        cache = cache_dir / "dynmap-markers"
        AirContext.__init__(self)
        Source.__init__(self)

        json = msgspec.json.decode(
            get_url(
                "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json", cache, timeout=timeout
            )
        )["sets"]["airports"]["markers"]

        for k, v in json.items():
            self.get_airport(code=k, coordinates=Sourced((v["x"], v["z"])).source(self))

        self.update()
