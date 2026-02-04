from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source



class CVCExpressCoord(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, CVCExpress)"
    priority = 1

    file_path = Path(__file__).parent / "cvc_express.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder
