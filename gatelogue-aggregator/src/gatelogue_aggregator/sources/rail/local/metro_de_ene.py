from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class MetroDeEne(RailYaml2Source):
    name = "Gatelogue (Rail, Metro de Eñe)"
    file_path = Path(__file__).parent / "metro_de_ene.yaml"
