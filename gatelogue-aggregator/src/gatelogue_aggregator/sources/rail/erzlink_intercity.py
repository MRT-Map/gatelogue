from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class ErzLinkIntercity(RailYaml2Source):
    name = "Gatelogue (Rail, ErzLink Intercity)"
    file_path = Path(__file__).parent / "erzlink_intercity.yaml"
