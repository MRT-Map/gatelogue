from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation


class FLRKaze(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, FLR Kazeshima/Shui Chau)"
    priority = 1

    file_path = Path(__file__).parent / "flr_kaze.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder

    def routing(self, line_node: RailLine, stations: list[RailStation], line_yaml: YamlLine):
        if line_node.code == "C1":
            self.B(self, line_node).connect(
                *stations,
                exclude=["Ho Kok West"],
                forward_direction=line_yaml.forward_label,
                backward_direction=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                *stations,
                between=("Ho Kok West", "Ho Kok"),
                forward_direction=line_yaml.forward_label,
                backward_direction=line_yaml.backward_label,
            )
        else:
            raise NotImplementedError
