from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class LavaRail(RailYaml2Source):
    name = "Gatelogue (Rail, Lava Rail)"
    file_path = Path(__file__).parent / "lava_rail.yaml"
