from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.source import AirSource

if TYPE_CHECKING:
    from gatelogue_aggregator.config import Config


class DynmapAirports(AirSource):
    name = "MRT Dynmap (Air)"
    json1: dict
    json2: dict

    def prepare(self, config: Config):
        cache1 = config.cache_dir / "dynmap-markers-new"
        cache2 = config.cache_dir / "dynmap-markers-old"

        response1 = get_url(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json",
            cache1,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        response2 = get_url(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_old.json",
            cache2,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        try:
            self.json1 = msgspec.json.decode(response1)["sets"]["airports"]["markers"]
            self.json2 = msgspec.json.decode(response2)["sets"]["airports"]["markers"]
        except Exception as e:
            raise ValueError(response1[:100], response2[:100]) from e

    def build(self, config: Config):
        for json, world in ((self.json1, "New"), (self.json2, "Old")):
            for k, v in json.items():
                name = v["label"].split("(")[0]
                self.airport(
                    code=next(reversed(k.split("-"))),
                    world=world,
                    coordinates=(v["x"], v["z"]),
                    names={name},
                )
