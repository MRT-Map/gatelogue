from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import RailYaml2Source


class SEATWarp(RailYaml2Source):
    name = "Gatelogue (Rail, SEAT)"
    file_path = Path(__file__).parent / "seat.yaml"
