from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation


class MarbleRailCoord(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, MarbleRail)"
    priority = 1

    file_path = Path(__file__).parent / "marblerail.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder
