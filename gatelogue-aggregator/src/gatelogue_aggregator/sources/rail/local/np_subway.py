from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.line_builder import RailLineBuilder, BusLineBuilder, SeaLineBuilder
from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine, RailYaml2Source, YamlRoute
import gatelogue_types as gt


class NPSubway(RailYaml2Source):
    name = "Gatelogue (Rail, New Prubourne Subway)"
    file_path = Path(__file__).parent / "np_subway.yaml"

    def routing(
        self,
        line_node: gt.RailLine,
        builder: RailLineBuilder,
        line_yaml: YamlLine,
        route_yaml: YamlRoute,
        cp: RailYaml2Source._ConnectParams,
    ):
        if line_node.code == "B":
            builder2 = builder.copy()
            builder2.connect_to("Penn Island-Zoo")
            builder2.connect_to("Evergreen Parkway")
        super().routing(line_node, builder, line_yaml, route_yaml, cp)
