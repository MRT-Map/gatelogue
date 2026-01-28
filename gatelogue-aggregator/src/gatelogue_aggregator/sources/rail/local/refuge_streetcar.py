from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation
from gatelogue_aggregator.utils import get_stn


class RefugeStreetcar(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, Refuge Streetcar)"
    priority = 1

    file_path = Path(__file__).parent / "refuge_streetcar.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder

    def routing(self, line_node: RailLine, stations: list[RailStation], line_yaml: YamlLine):
        if line_node.code == "North/South Loop":
            self.B(self, line_node).connect(
                get_stn(stations, "West Train Station"), stations[0], forward_direction="Anticlockwise", one_way=True
            )
            self.B(self, line_node).connect(
                *stations, between=(None, "West Train Station"), forward_direction="Anticlockwise", one_way=True
            )
            self.B(self, line_node).connect(
                *stations,
                between=("West Train Station", "South Hill"),
                forward_direction="Southbound",
                backward_direction="Northbound",
            )
            self.B(self, line_node).connect(
                *stations,
                between=("South Hill", None),
                forward_direction="Anticlockwise",
                one_way=True,
            )
            self.B(self, line_node).connect(
                stations[-1],
                get_stn(stations, "South Hill"),
                forward_direction="Anticlockwise",
                one_way=True,
            )
        else:
            self.B(self, line_node).circle(*stations, forward_label="Clockwise", backward_label="Anticlockwise")
