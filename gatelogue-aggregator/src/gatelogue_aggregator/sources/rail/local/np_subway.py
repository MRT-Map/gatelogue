from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation
from gatelogue_aggregator.utils import get_stn


class NPSubway(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, New Prubourne Subway)"
    priority = 1

    file_path = Path(__file__).parent / "np_subway.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder

    def custom_routing(self, line_node: RailLine, stations: list[RailStation], line_yaml: YamlLine):
        if line_node.code == "B":
            self.B(self, line_node).connect(
                *stations,
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                get_stn(stations, "Penn Island-Zoo"),
                get_stn(stations, "Evergreen Parkway"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
        else:
            raise NotImplementedError
