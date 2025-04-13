from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine
from gatelogue_aggregator.types.node.bus import BusLine, BusStop
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation
from gatelogue_aggregator.types.node.sea import SeaLine, SeaStop


class FLRKaze(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, FLR Kazeshima/Shui Chau)"
    priority = 1

    file_path = Path(__file__).parent / "flr_kaze.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder

    def custom_routing(self, line_node: RailLine, stations: list[RailStation], line_yaml: YamlLine):
        if line_node.code == "C1":
            self.B(self, line_node).connect(
                *stations,
                exclude=["Ho Kok West"],
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                *stations,
                between=("Ho Kok West", "Ho Kok"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
        raise NotImplementedError
