from __future__ import annotations

from typing import TYPE_CHECKING

from gatelogue_aggregator.downloader import get_json
from gatelogue_aggregator.source import AirSource
from gatelogue_aggregator.sources.dynmap_markers import DynmapMarkers

if TYPE_CHECKING:
    from gatelogue_aggregator.config import Config


class DynmapAirports(AirSource):
    name = "MRT Dynmap (Air)"

    def build(self, config: Config):
        for json, world in ((DynmapMarkers.new, "New"), (DynmapMarkers.old, "Old")):
            json = json["airports"]["markers"]
            for k, v in json.items():
                name = v["label"].split("(")[0]
                self.airport(
                    code=next(reversed(k.split("-"))),
                    world=world,
                    coordinates=(v["x"], v["z"]),
                    names={name},
                )
