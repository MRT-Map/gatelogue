from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class PacificaCoord(RailYaml2Source):
    name = "Gatelogue (Rail, Pacifica)"
    file_path = Path(__file__).parent / "pacifica.yaml"
