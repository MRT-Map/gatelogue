from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import BusYaml2Source


class Midwestern(BusYaml2Source):
    name = "Gatelogue (Bus, Midwestern Bus Services)"
    file_path = Path(__file__).parent / "midwestern.yaml"
