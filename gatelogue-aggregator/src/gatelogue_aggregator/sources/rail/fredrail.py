from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine


if TYPE_CHECKING:
    from gatelogue_aggregator.types.node.bus import BusLine, BusStop
    from gatelogue_aggregator.types.node.sea import SeaLine, SeaStop


class FredRail(Yaml2Source, RailSource):
    name = "Gatelogue (Rail, Fred Rail)"
    priority = 1

    file_path = Path(__file__).parent / "fredrail.yaml"
    C = RailCompany
    L = RailLine
    S = RailStation
    B = RailLineBuilder

    def routing(
        self,
        line_node: RailLine | BusLine | SeaLine,
        stations: list[RailStation | BusStop | SeaStop],
        _line_yaml: YamlLine,
    ):
        if line_node.name.v == "New Jerseyan":
            forward_label = "towards Boston Waterloo"
            backward_label = "towards Rattlerville Central"
            RailLineBuilder(self, line_node).connect(
                *stations[:3], forward_direction=forward_label, backward_direction=backward_label
            )
            RailLineBuilder(self, line_node).connect(
                *stations[2:5], forward_direction=forward_label, backward_direction=backward_label, one_way=True
            )
            RailLineBuilder(self, line_node).connect(
                stations[4],
                stations[2],
                forward_direction=backward_label,
                backward_direction=forward_label,
                one_way=True,
            )
            RailLineBuilder(self, line_node).connect(
                *stations[4:], forward_direction=forward_label, backward_direction=backward_label
            )
            return
        raise NotImplementedError
