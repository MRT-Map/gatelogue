from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import get_json
from gatelogue_aggregator.logging import INFO1, progress_bar


class DynmapMarkers:
    old: dict
    new: dict

    @classmethod
    def prepare(cls, config: Config):
        with progress_bar(INFO1, "Downloading markers from MRT Dynmap"):
            cls.new = get_json(
                "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json",
                "dynmap-markers-new",
                config,
            )["sets"]
            cls.old = get_json(
                "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_old.json",
                "dynmap-markers-old",
                config,
            )["sets"]
