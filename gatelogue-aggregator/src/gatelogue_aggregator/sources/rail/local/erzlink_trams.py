from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.line_builder import RailLineBuilder, BusLineBuilder, SeaLineBuilder
from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine, RailYaml2Source, YamlRoute
import gatelogue_types as gt


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
