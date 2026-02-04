from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, RailYaml2Source


class RaiLinQWarp(RailYaml2Source):
    name = "Gatelogue (Rail, RaiLinQ)"
    file_path = Path(__file__).parent / "railinq.yaml"