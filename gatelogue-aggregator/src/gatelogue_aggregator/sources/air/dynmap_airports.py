from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from gatelogue_aggregator.downloader import get_url, get_json
from gatelogue_aggregator.source import AirSource

if TYPE_CHECKING:
    from gatelogue_aggregator.config import Config


class DynmapAirports(AirSource):
    name = "MRT Dynmap (Air)"
    json1: dict
    json2: dict

    def prepare(self, config: Config):
        response1 = get_json(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json",
            "dynmap-markers-new", config
        )
        response2 = get_json(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_old.json",
            "dynmap-markers-old", config
        )
        try:
            self.json1 = response1["sets"]["airports"]["markers"]
            self.json2 = response2["sets"]["airports"]["markers"]
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
