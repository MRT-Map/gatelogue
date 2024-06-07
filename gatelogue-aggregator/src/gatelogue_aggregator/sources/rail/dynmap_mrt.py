import re
from pathlib import Path

import msgspec
import rich
import rich.progress

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.rail import RailContext, RailSource


class DynmapMRT(RailSource):
    name = "MRT Dynmap (Rail, MRT)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        cache1 = cache_dir / "dynmap-markers-new"
        cache2 = cache_dir / "dynmap-markers-old"
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="MRT")

        response1 = get_url(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json", cache1, timeout=timeout
        )
        response2 = get_url(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_old.json", cache2, timeout=timeout
        )
        try:
            json1 = msgspec.json.decode(response1)["sets"]
            json2 = msgspec.json.decode(response2)["sets"]
        except Exception as e:
            raise ValueError(response1[:100], response2[:100]) from e

        for v in rich.progress.track(json1.values(), "Extracting from markers", transient=True):
            if len(v["markers"]) == 0:
                continue
            if (result := re.search(r"\[(?P<code>.*?)] (?P<name>.*)", v["label"])) is None:
                continue
            line_code = result.group("code").strip()

            for k, vv in v["markers"].items():
                code = k.upper()
                coordinates = (vv["x"], vv["z"])
                name = None if (result := re.search(r"(.*) \((.*?)\)", vv["label"])) is None else result.group(1)
                self.station(codes={code}, company=company, coordinates=coordinates, name=name, world="New")
            rich.print(f"[green]  MRT {line_code} has {len(v['markers'])} stations")

        for k, v in json2["old"]["markers"].items():
            code = "Old-" + k.upper()
            coordinates = (v["x"], v["z"])
            name = None if (result := re.search(r"(.*) \((.*?)\)", v["label"])) is None else result.group(1)
            self.station(codes={code}, company=company, coordinates=coordinates, name=name, world="Old")
        rich.print(f"[green]  Old world has {len(json2['old']['markers'])} stations")
