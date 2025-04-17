from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

import msgspec
import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.context.proximity import Proximity
from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusLineBuilder, BusSource, BusStop
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailMode,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaMode, SeaSource, SeaStop
from gatelogue_aggregator.types.source import Source

if TYPE_CHECKING:
    from pathlib import Path

    from gatelogue_aggregator.types.config import Config


class YamlLine(msgspec.Struct):
    name: str
    stations: list[str | tuple[str, str]]

    forward_label: str | None = None
    backward_label: str | None = None
    colour: str | None = None
    mode: str | None = None
    code: str | None = None


class Yaml(msgspec.Struct):
    company_name: str
    lines: list[YamlLine] = msgspec.field(default_factory=list)
    coords: dict[str, tuple[int, int]] = msgspec.field(default_factory=dict)
    merge_codes: list[set[str]] = msgspec.field(default_factory=list)
    proximity: list[set[str]] = msgspec.field(default_factory=list)

    local: bool = False
    colour: str | None = None
    mode: RailMode | SeaMode = "warp"
    world: str = "New"


class Yaml2Source(RailSource, BusSource, SeaSource):
    name = "Gatelogue"
    priority = 0

    file_path: Path
    C: type[RailCompany | BusCompany | SeaCompany]
    L: type[RailLine | BusLine | SeaLine]
    S: type[RailStation | BusStop | SeaStop]
    B: type[RailLineBuilder | BusLineBuilder | SeaLineBuilder]

    def __init__(self, config: Config):
        BaseContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        with self.file_path.open() as f:
            file = msgspec.yaml.decode(f.read(), type=Yaml)

        company = self.C.new(self, name=file.company_name, local=file.local)

        for codes in file.merge_codes:
            self.S.new(
                self,
                codes=codes,
                company=company,
            )

        for line in file.lines:
            line_node = self.L.new(
                self,
                code=line.code or line.name,
                name=line.name,
                colour=line.colour or file.colour,
                company=company,
            )
            if hasattr(line_node, "mode"):
                line_node.mode = self.source(line.mode)
            stations = [
                self.S.new(
                    self,
                    codes={a[0] if isinstance(a, tuple) else a},
                    name=a[1] if isinstance(a, tuple) else a,
                    company=company,
                )
                for a in line.stations
            ]
            try:
                self.custom_routing(line_node, stations, line)
            except NotImplementedError:
                self.B(self, line_node).connect(
                    *stations, forward_label=line.forward_label, backward_label=line.backward_label
                )

            rich.print(RESULT + f"{file.company_name} {line.code or line.name} has {len(stations)} stations")

        for code, (x, z) in file.coords.items():
            self.S.new(
                self,
                codes={code},
                company=company,
                world="New",
                coordinates=(x, z),
            )

        for set_ in file.proximity:
            for code1, code2 in itertools.combinations(set_, 2):
                st1 = self.S.new(self, codes={code1}, company=company)
                st2 = self.S.new(self, codes={code2}, company=company)
                x1, y1 = file.coords[code1]
                x2, y2 = file.coords[code2]
                st1.connect(self, st2, Proximity(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5, explicit=True))

        self.save_to_cache(config, self.g)

    def custom_routing(
        self,
        line_node: RailLine | BusLine | SeaLine,
        stations: list[RailStation | BusStop | SeaStop],
        line_yaml: YamlLine,
    ):
        raise NotImplementedError
