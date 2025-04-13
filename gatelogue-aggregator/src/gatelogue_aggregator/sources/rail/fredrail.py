from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.yaml2source import Yaml2Source
from gatelogue_aggregator.types.node.rail import RailCompany, RailLine, RailLineBuilder, RailSource, RailStation

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

    def custom_routing(self, line_node: RailLine | BusLine | SeaLine, stations: list[RailStation | BusStop | SeaStop], _):
        if line_node.name.v == "New Jerseyan":
            forward_label = "towards Boston Waterloo"
            backward_label = "towards Rattlerville Central"
            RailLineBuilder(self, line_node).connect(
                *stations[:3], forward_label=forward_label, backward_label=backward_label
            )
            RailLineBuilder(self, line_node).connect(
                *stations[2:5], forward_label=forward_label, backward_label=backward_label, one_way=True
            )
            RailLineBuilder(self, line_node).connect(
                stations[4], stations[2], forward_label=backward_label, backward_label=forward_label, one_way=True
            )
            RailLineBuilder(self, line_node).connect(
                *stations[4:], forward_label=forward_label, backward_label=backward_label
            )
            return
        raise NotImplementedError
