import msgspec

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.air import AirAirport, AirSource
from gatelogue_aggregator.types.source import Source


class DynmapAirports(AirSource):
    name = "MRT Dynmap (Air)"
    priority = 0

    def __init__(self, config: Config):
        cache1 = config.cache_dir / "dynmap-markers-new"
        cache2 = config.cache_dir / "dynmap-markers-old"
        AirSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        response1 = get_url(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json",
            cache1,
            timeout=config.timeout,
        )
        response2 = get_url(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_old.json",
            cache2,
            timeout=config.timeout,
        )
        try:
            json1 = msgspec.json.decode(response1)["sets"]["airports"]["markers"]
            json2 = msgspec.json.decode(response2)["sets"]["airports"]["markers"]
        except Exception as e:
            raise ValueError(response1[:100], response2[:100]) from e

        for json, world in ((json1, "New"), (json2, "Old")):
            for k, v in json.items():
                name = reversed(v["label"].split("(")[0].split("-"))[0]
                AirAirport.new(
                    self, code=AirAirport.process_code(k), world=world, coordinates=(v["x"], v["z"]), name=name
                )

        self.save_to_cache(config, self.g)
