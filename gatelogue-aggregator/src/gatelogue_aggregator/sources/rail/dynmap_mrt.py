import re

import msgspec

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.logging import INFO3, track
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource


class DynmapMRT(RailSource):
    name = "MRT Dynmap (Rail, MRT)"
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
            self.json1 = msgspec.json.decode(response1)["sets"]
            self.json2 = msgspec.json.decode(response2)["sets"]
        except Exception as e:
            raise ValueError(response1[:100], response2[:100]) from e

    def build(self, config: Config):
        company = self.company(name="MRT")

        for v in track(self.json1.values(), INFO3, description="Extracting from markers"):
            if len(v["markers"]) == 0:
                continue
            if (result := re.search(r"\[(?P<code>.*?)] (?P<name>.*)", v["label"])) is None:
                continue
            result.group("code").strip()

            for k, vv in v["markers"].items():
                code = k.upper()
                if code == "M0":
                    code = "MW"
                elif code == "MS":
                    code = "MH"
                coordinates = (vv["x"], vv["z"])
                name = None if (result := re.search(r"(.*) \((.*?)\)", vv["label"])) is None else result.group(1)
                if name is not None:
                    name = name.strip().removesuffix("Station")
                self.station(codes={code}, company=company, coordinates=coordinates, name=name, world="New")

        for k, v in self.json2["old"]["markers"].items():
            code = "Old-" + k.upper()
            coordinates = (v["x"], v["z"])
            name = None if (result := re.search(r"(.*) \((.*?)\)", v["label"])) is None else result.group(1).strip()
            self.station(codes={code}, company=company, coordinates=coordinates, name=name, world="Old")
