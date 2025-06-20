from __future__ import annotations

from typing import TYPE_CHECKING, override

import msgspec

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.types.node.air import AirAirport, AirSource

if TYPE_CHECKING:
    from gatelogue_aggregator.types.config import Config
    from gatelogue_aggregator.types.node.base import Node


class DynmapAirports(AirSource):
    name = "MRT Dynmap (Air)"
    priority = 0

    @classmethod
    @override
    def reported_nodes(cls) -> tuple[type[Node], ...]:
        return (AirAirport,)

    def build(self, config: Config):
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
            json1 = msgspec.json.decode(response1)["sets"]["airports"]["markers"]
            json2 = msgspec.json.decode(response2)["sets"]["airports"]["markers"]
        except Exception as e:
            raise ValueError(response1[:100], response2[:100]) from e

        for json, world in ((json1, "New"), (json2, "Old")):
            for k, v in json.items():
                name = v["label"].split("(")[0]
                AirAirport.new(
                    self,
                    code=AirAirport.process_code(next(reversed(k.split("-")))),
                    world=world,
                    coordinates=(v["x"], v["z"]),
                    names={name},
                )
