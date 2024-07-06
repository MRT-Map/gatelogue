import re

import msgspec
import rich
import rich.progress

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.logging import INFO3, RESULT, track
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class DynmapMRT(RailSource):
    name = "MRT Dynmap (Rail, MRT)"
    priority = 1

    def __init__(self, config: Config):
        cache1 = config.cache_dir / "dynmap-markers-new"
        cache2 = config.cache_dir / "dynmap-markers-old"
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="MRT")

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
            json1 = msgspec.json.decode(response1)["sets"]
            json2 = msgspec.json.decode(response2)["sets"]
        except Exception as e:
            raise ValueError(response1[:100], response2[:100]) from e

        for v in track(json1.values(), description=INFO3 + "Extracting from markers"):
            if len(v["markers"]) == 0:
                continue
            if (result := re.search(r"\[(?P<code>.*?)] (?P<name>.*)", v["label"])) is None:
                continue
            line_code = result.group("code").strip()

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
                self.rail_station(codes={code}, company=company, coordinates=coordinates, name=name, world="New")
            rich.print(RESULT + f"MRT {line_code} has {len(v['markers'])} stations")

        for k, v in json2["old"]["markers"].items():
            code = "Old-" + k.upper()
            coordinates = (v["x"], v["z"])
            name = None if (result := re.search(r"(.*) \((.*?)\)", v["label"])) is None else result.group(1)
            self.rail_station(codes={code}, company=company, coordinates=coordinates, name=name, world="Old")
        rich.print(RESULT + f"Old world has {len(json2['old']['markers'])} stations")
        self.save_to_cache(config, self.g)
