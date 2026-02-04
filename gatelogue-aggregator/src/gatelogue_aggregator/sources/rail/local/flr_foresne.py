from __future__ import annotations

from pathlib import Path

import gatelogue_types as gt

from gatelogue_aggregator.sources.line_builder import RailLineBuilder
from gatelogue_aggregator.sources.yaml2source import RailYaml2Source, YamlLine, YamlRoute


class FLRForesne(RailYaml2Source):
    name = "Gatelogue (Rail, FLR Foresne)"
    file_path = Path(__file__).parent / "flr_foresne.yaml"

    def routing(
        self,
        line_node: gt.RailLine,
        builder: RailLineBuilder,
        line_yaml: YamlLine,
        route_yaml: YamlRoute,
        cp: RailYaml2Source._ConnectParams,
    ):
        if line_node.code == "4":
            builder.connect(until="Suspension Hill", **cp)
            builder.skip(until="Cinnameadow", detached=True)
            builder.connect(**cp)
        else:
            super().routing(line_node, builder, line_yaml, route_yaml, cp)
