from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusLineBuilder, BusSource, BusStop
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop
from gatelogue_aggregator.types.source import Source

if TYPE_CHECKING:
    from pathlib import Path

    from gatelogue_aggregator.types.config import Config


class YamlLine(msgspec.Struct):
    name: str
    stations: list[str | tuple[str, str]]

    forward_label: str = None
    backward_label: str = None
    custom_routing: bool = False
    colour: str | None = None
    mode: str | None = None
    code: str | None = None


class Yaml(msgspec.Struct):
    company_name: str
    coords: dict[str, tuple[int, int]]
    lines: list[YamlLine]

    colour: str | None = None
    mode: str = "warp"


class Yaml2Source(RailSource, BusSource, SeaSource):
    name = "MRT Wiki (Rail, SEAT)"
    priority = 1

    C: type[RailCompany | BusCompany | SeaCompany]
    L: type[RailLine | BusLine | SeaLine]
    S: type[RailStation | BusStop | SeaStop]
    B: type[RailLineBuilder | BusLineBuilder | SeaLineBuilder]

    def __init__(self, config: Config, file_path: Path):
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        with file_path.open() as f:
            file = msgspec.yaml.decode(f.read(), type=Yaml)

        company = self.C.new(self, name=file.company_name)

        for line in file.lines:
            line_node = self.L.new(
                self,
                code=line.code or line.name,
                name=line.name,
                mode=line.mode or file.mode,
                colour=line.colour or file.colour,
                company=company,
            )
            stations = [
                self.S.new(
                    self,
                    codes={a[0]} if isinstance(a, tuple) else a,
                    name=a[1] if isinstance(a, tuple) else a,
                    company=company,
                )
                for a in line.stations
            ]
            if line.custom_routing:
                self.custom_routing(line_node, stations)
            else:
                self.B(self, line_node).connect(
                    *stations, forward_label=line.forward_label, backward_label=line.backward_label
                )

        self.save_to_cache(config, self.g)

    def custom_routing(self, line_node: RailLine | BusLine | SeaLine, stations: list[RailStation | BusStop | SeaStop]):
        raise NotImplementedError
