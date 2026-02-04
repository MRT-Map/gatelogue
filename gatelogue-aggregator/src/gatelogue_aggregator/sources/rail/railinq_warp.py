from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source



class RaiLinQWarp(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, RaiLinQ)"
    priority = 1

    file_path = Path(__file__).parent / "railinq.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder
