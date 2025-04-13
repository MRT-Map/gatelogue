from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation
from gatelogue_aggregator.utils import get_stn


class FLRForesne(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, FLR Foresne)"
    priority = 1

    file_path = Path(__file__).parent / "flr_foresne.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder

    def custom_routing(self, line_node: RailLine, stations: list[RailStation], line_yaml: YamlLine):
        if line_node.code == "4":
            self.B(self, line_node).connect(
                *stations,
                between=(None, "Suspension Hill"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                get_stn(stations, "Cinnameadow"),
                get_stn(stations, "North Plaxaëten"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
                one_way=True,
            )
            self.B(self, line_node).connect(
                *reversed(stations),
                between=(None, "Cinnameadow"),
                forward_label=line_yaml.backward_label,
                backward_label=line_yaml.forward_label,
                one_way=True,
            )
        else:
            raise NotImplementedError
