import re

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import get_json
from gatelogue_aggregator.logging import INFO3, track
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.dynmap_markers import DynmapMarkers


class DynmapMRT(RailSource):
    name = "MRT Dynmap (Rail, MRT)"

    def build(self, config: Config):
        company = self.company(name="MRT")

        for v in track(DynmapMarkers.new.values(), INFO3, description="Extracting from markers"):
            if len(v["markers"]) == 0:
                continue
            if re.search(r"\[(?P<code>.*?)] (?P<name>.*)", v["label"]) is None:
                continue

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

        for k, v in DynmapMarkers.old["old"]["markers"].items():
            code = "Old-" + k.upper()
            coordinates = (v["x"], v["z"])
            name = None if (result := re.search(r"(.*) \((.*?)\)", v["label"])) is None else result.group(1).strip()
            self.station(codes={code}, company=company, coordinates=coordinates, name=name, world="Old")
