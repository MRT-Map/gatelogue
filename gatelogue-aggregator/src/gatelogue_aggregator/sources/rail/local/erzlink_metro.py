from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation


class ErzLinkMetro(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, ErzLink Metro)"
    priority = 1

    file_path = Path(__file__).parent / "erzlink_metro.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder

    def custom_routing(self, line_node: RailLine, stations: list[RailStation], line_yaml: YamlLine):
        if line_node.code == "6":
            self.B(self, line_node).connect(
                *stations, between=(None, "Riverdane"), forward_label=line_yaml.forward_label, backward_label=line_yaml.backward_label
            )
            self.B(self, line_node).connect(
                *stations, between=("Crowood", None), forward_label=line_yaml.forward_label, backward_label=line_yaml.backward_label
            )
        elif line_node.code == "6 Express":
            self.B(self, line_node).connect(
                *stations, between=(None, "Essex Central"), forward_label=line_yaml.forward_label, backward_label=line_yaml.backward_label
            )
            self.B(self, line_node).connect(
                *stations, between=("New Erzville", None), forward_label=line_yaml.forward_label, backward_label=line_yaml.backward_label
            )
        else:
            raise NotImplementedError
