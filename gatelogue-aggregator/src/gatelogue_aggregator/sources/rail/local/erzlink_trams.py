from __future__ import annotations

from pathlib import Path

import gatelogue_types as gt

from gatelogue_aggregator.sources.line_builder import RailLineBuilder
from gatelogue_aggregator.sources.yaml2source import RailYaml2Source, YamlLine, YamlRoute


class ErzLinkTrams(RailYaml2Source):
    name = "Gatelogue (Rail, ErzLink Trams)"
    file_path = Path(__file__).parent / "erzlink_trams.yaml"

    def routing(
        self,
        line_node: gt.RailLine,
        builder: RailLineBuilder,
        line_yaml: YamlLine,
        route_yaml: YamlRoute,
        cp: RailYaml2Source._ConnectParams,
    ):
        if line_node.code == "0":
            builder.connect_circle(**cp)
        elif line_node.code == "X2a":
            builder.connect(until="Euneva Interchange", **cp)
            builder.skip(until="Shellwater Plaza")
            builder.connect(**cp)
        else:
            super().routing(line_node, builder, line_yaml, route_yaml, cp)
