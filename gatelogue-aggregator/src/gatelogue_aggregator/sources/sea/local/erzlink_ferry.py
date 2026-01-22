from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.yaml2source import Yaml2Source
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop


class ErzLinkFerry(Yaml2Source, SeaSource):
    name = "Gatelogue (Sea, ErzLink Ferry)"
    priority = 1

    file_path = Path(__file__).parent / "erzlink_ferry.yaml"
    C = SeaCompany
    L = SeaLine
    S = SeaStop
    B = SeaLineBuilder
