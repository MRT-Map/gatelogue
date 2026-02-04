from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class FLRSheng(RailYaml2Source):
    name = "Gatelogue (Rail, FLR Shenghua)"
    file_path = Path(__file__).parent / "flr_sheng.yaml"
