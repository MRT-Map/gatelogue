from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class MarbleRailCoord(RailYaml2Source):
    name = "Gatelogue (Rail, MarbleRail)"
    file_path = Path(__file__).parent / "marblerail.yaml"
