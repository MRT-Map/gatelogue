from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.line_builder import RailLineBuilder, BusLineBuilder, SeaLineBuilder
from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine, RailYaml2Source, YamlRoute
import gatelogue_types as gt



class FLRSheng(RailYaml2Source):
    name = "Gatelogue (Rail, FLR Shenghua)"
    file_path = Path(__file__).parent / "flr_sheng.yaml"
