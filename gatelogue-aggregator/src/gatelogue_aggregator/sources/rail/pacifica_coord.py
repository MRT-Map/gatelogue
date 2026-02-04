from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source



class PacificaCoord(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, Pacifica)"
    priority = 1

    file_path = Path(__file__).parent / "pacifica.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder
