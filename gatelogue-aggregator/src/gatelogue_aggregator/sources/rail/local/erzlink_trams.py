from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation
from gatelogue_aggregator.utils import get_stn


class ErzLinkTrams(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, ErzLink Trams)"
    priority = 1

    file_path = Path(__file__).parent / "erzlink_trams.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder

    def custom_routing(self, line_node: RailLine, stations: list[RailStation], line_yaml: YamlLine):
        if line_node.code == "0":
            self.B(self, line_node).circle(
                *stations, forward_label=line_yaml.forward_label, backward_label=line_yaml.backward_label
            )
        elif line_node.code == "3":
            self.B(self, line_node).connect(
                *stations,
                between=(None, "Atrium North"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                *stations,
                between=("Atrium South", None),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                get_stn(stations, "Atrium North"),
                get_stn(stations, "Atrium East"),
                get_stn(stations, "Atrium South"),
                one_way=True,
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                get_stn(stations, "Atrium South"),
                get_stn(stations, "Atrium West"),
                get_stn(stations, "Atrium North"),
                one_way=True,
                forward_label=line_yaml.backward_label,
                backward_label=line_yaml.forward_label,
            )
        elif line_node.code == "X2a":
            self.B(self, line_node).connect(
                *stations,
                between=(None, "Euneva Interchange"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                *stations,
                between=("Shellwater Plaza", None),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
        else:
            raise NotImplementedError
