from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import gatelogue_types as gt
from gatelogue_aggregator.sources.line_builder import RailLineBuilder, BusLineBuilder, SeaLineBuilder

from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine, RailYaml2Source, YamlRoute


class FredRail(RailYaml2Source):
    name = "Gatelogue (Rail, Fred Rail)"
    file_path = Path(__file__).parent / "fredrail.yaml"