from __future__ import annotations

from pathlib import Path

import gatelogue_types as gt

from gatelogue_aggregator.sources.line_builder import SeaLineBuilder
from gatelogue_aggregator.sources.yaml2source import SeaYaml2Source, YamlLine, YamlRoute


class ErzLinkFerry(SeaYaml2Source):
    name = "Gatelogue (Sea, ErzLink Ferry)"
    file_path = Path(__file__).parent / "erzlink_ferry.yaml"

    def routing(
        self,
        line_node: gt.SeaLine,
        builder: SeaLineBuilder,
        line_yaml: YamlLine,
        route_yaml: YamlRoute,
        cp: SeaYaml2Source._ConnectParams,
    ):
        cp["forward_direction"] = cp["backward_direction"] = None
        builder.connect(**cp)
