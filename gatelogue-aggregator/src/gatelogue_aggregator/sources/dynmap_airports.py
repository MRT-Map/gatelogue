from pathlib import Path

import msgspec

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.types.air import AirContext, AirSource
from gatelogue_aggregator.types.base import Source, process_airport_code


class DynmapAirports(AirSource):
    name = "MRT Dynmap"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        cache1 = cache_dir / "dynmap-markers-new"
        cache2 = cache_dir / "dynmap-markers-old"
        AirContext.__init__(self)
        Source.__init__(self)

        response1 = get_url(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json", cache1, timeout=timeout
        )
        response2 = get_url(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_old.json", cache2, timeout=timeout
        )
        try:
            json = (
                msgspec.json.decode(response1)["sets"]["airports"]["markers"]
                | msgspec.json.decode(response2)["sets"]["airports"]["markers"]
            )
        except Exception as e:
            raise ValueError(response1[:100], response2[:100]) from e

        for k, v in json.items():
            self.airport(code=process_airport_code(k), coordinates=(v["x"], v["z"]))
