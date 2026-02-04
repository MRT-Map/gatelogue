from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source



class LavaRail(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, Lava Rail)"
    priority = 1

    file_path = Path(__file__).parent / "lava_rail.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder
