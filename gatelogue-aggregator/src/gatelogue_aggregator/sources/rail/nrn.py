from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, RailYaml2Source


class NRN(RailYaml2Source):
    name = "Gatelogue (Rail, NRN)"
    file_path = Path(__file__).parent / "nrn.yaml"
