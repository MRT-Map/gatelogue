from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class NSC(RailYaml2Source):
    name = "Gatelogue (Rail, Network South Central)"
    file_path = Path(__file__).parent / "nsc.yaml"
