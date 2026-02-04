from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class FredRail(RailYaml2Source):
    name = "Gatelogue (Rail, Fred Rail)"
    file_path = Path(__file__).parent / "fredrail.yaml"
