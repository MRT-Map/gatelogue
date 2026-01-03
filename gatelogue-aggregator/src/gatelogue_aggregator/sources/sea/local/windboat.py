from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop
from gatelogue_aggregator.utils import get_stn


class Windboat(Yaml2Source, SeaSource):
    name = "Gatelogue (Sea, Windboat)"
    priority = 1

    file_path = Path(__file__).parent / "windboat.yaml"
    C = SeaCompany
    L = SeaLine
    S = SeaStop
    B = SeaLineBuilder

    def custom_routing(self, line_node: SeaLine, stations: list[SeaStop], line_yaml: YamlLine):
        if line_node.code == "KN":
            self.B(self, line_node).connect(
                *stations,
                between=(None, "Wenyanga"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                *stations[::2],
                between=(None, "Wenyanga"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                *stations[1::2],
                between=(None, "Anseijima"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )

            self.B(self, line_node).connect(
                get_stn(stations, "Kita-kengiguntō"),
                get_stn(stations, "Triangle Archipelago"),
                get_stn(stations, "Macece Island"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                get_stn(stations, "Kita-kengiguntō"),
                get_stn(stations, "Macece Island"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                get_stn(stations, "Minami-kengiguntō"),
                get_stn(stations, "Triangle Archipelago"),
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
        elif line_node.code == "HE":
            self.B(self, line_node).circle(
                *stations,
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).circle(
                *stations[::2],
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).circle(
                *stations[1::2],
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
        else:
            self.B(self, line_node).connect(
                *stations,
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                *stations[::2],
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
            self.B(self, line_node).connect(
                *stations[1::2],
                forward_label=line_yaml.forward_label,
                backward_label=line_yaml.backward_label,
            )
