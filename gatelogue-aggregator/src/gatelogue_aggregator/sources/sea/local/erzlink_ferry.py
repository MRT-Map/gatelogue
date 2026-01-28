from __future__ import annotations

from pathlib import Path
from typing import Literal

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
        one_way: dict[str, Literal["forwards", "backwards"]] | None,
        platform_codes: dict[str, tuple[str | None, str | None]] | None,
    ):
        builder.connect(one_way=one_way, platform_codes=platform_codes, forward_direction=None, backward_direction=None)
