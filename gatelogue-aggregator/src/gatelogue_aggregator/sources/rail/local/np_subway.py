from __future__ import annotations

from pathlib import Path

import gatelogue_types as gt

from gatelogue_aggregator.sources.line_builder import RailLineBuilder
from gatelogue_aggregator.sources.yaml2source import RailYaml2Source, YamlLine, YamlRoute


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
            builder2.connect_to("Penn Island-Zoo", **cp)
            builder2.connect_to("Evergreen Parkway", **cp)
        super().routing(line_node, builder, line_yaml, route_yaml, cp)
