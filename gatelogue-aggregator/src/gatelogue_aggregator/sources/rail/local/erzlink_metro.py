from __future__ import annotations

from pathlib import Path

import gatelogue_types as gt

from gatelogue_aggregator.sources.line_builder import RailLineBuilder
from gatelogue_aggregator.sources.yaml2source import RailYaml2Source, YamlLine, YamlRoute


class ErzLinkMetro(RailYaml2Source):
    name = "Gatelogue (Rail, ErzLink Metro)"
    file_path = Path(__file__).parent / "erzlink_metro.yaml"

    def routing(
        self,
        line_node: gt.RailLine,
        builder: RailLineBuilder,
        line_yaml: YamlLine,
        route_yaml: YamlRoute,
        cp: RailYaml2Source._ConnectParams,
    ):
        if line_node.code == "6":
            builder.connect(until="Riverdane", **cp)
            builder.skip(until="Crowood", detached=True)
            builder.connect(**cp)
        elif line_node.code == "6 Express":
            builder.connect(until="Essex Central", **cp)
            builder.skip(until="New Erzville", detached=True)
            builder.connect(**cp)
        else:
            super().routing(line_node, builder, line_yaml, route_yaml, cp)
