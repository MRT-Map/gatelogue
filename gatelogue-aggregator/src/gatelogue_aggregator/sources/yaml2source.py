from __future__ import annotations

import itertools
import re
from typing import TYPE_CHECKING, ClassVar, Literal

import gatelogue_types as gt
import msgspec
import rich

from gatelogue_aggregator.source import RailSource, BusSource, SeaSource, Source
from gatelogue_aggregator.sources.line_builder import SeaLineBuilder, BusLineBuilder, RailLineBuilder
from gatelogue_types import node

from gatelogue_aggregator.logging import RESULT

if TYPE_CHECKING:
    from pathlib import Path

    from gatelogue_aggregator.config import Config

class YamlRoute(msgspec.Struct):
    stations: list[str]
    forward_direction: str | None = ""
    backward_direction: str | None = ""

class YamlLine(msgspec.Struct):
    name: str
    routing: list[YamlRoute] | None = None

    stations: list[str] | None = None
    forward_direction: str | None = ""
    backward_direction: str | None = ""
    # TODO mutually exclusive

    colour: str | None = None
    mode: gt.BusMode | gt.RailMode | gt.SeaMode | None = None
    code: str | None = None
    local: bool | None = None


class Yaml(msgspec.Struct):
    company_name: str
    lines: list[YamlLine] = msgspec.field(default_factory=list)
    coords: dict[str, tuple[int, int]] = msgspec.field(default_factory=dict)
    merge_codes: list[set[str]] = msgspec.field(default_factory=list)
    proximity: list[set[str]] = msgspec.field(default_factory=list)

    local: bool = False
    colour: str | None = None
    mode: gt.BusMode | gt.RailMode | gt.SeaMode | None = "warp"
    world: gt.World = "New"


class Yaml2Source(Source):
    name = "Gatelogue"

    file_path: ClassVar[Path]
    C: ClassVar[type[gt.RailCompany | gt.BusCompany | gt.SeaCompany]]
    L: ClassVar[type[gt.RailLine | gt.BusLine | gt.SeaLine]]
    S: ClassVar[type[gt.RailStation | gt.BusStop | gt.SeaStop]]
    P: ClassVar[type[gt.RailPlatform | gt.BusBerth | gt.SeaDock]]
    B: ClassVar[type[RailLineBuilder | BusLineBuilder | SeaLineBuilder]]

    def build(self, _config: Config):
        with self.file_path.open() as f:
            file = msgspec.yaml.decode(f.read(), type=Yaml)

        company = self.C.create(self.conn, self.priority, name=file.company_name)

        for codes in file.merge_codes:
            self.S.create(
                self.conn, self.priority,
                codes=codes,
                company=company,
            )

        for line in file.lines:
            line_node = self.L.create(
                self.conn, self.priority,
                code=line.code or line.name,
                name=line.name,
                colour=line.colour or file.colour,
                local=line.local or file.local,
                mode=line.mode or file.mode,
                company=company,
            )
            routing = line.routing or [YamlRoute(line.stations, line.forward_direction, line.backward_direction)]
            for route in routing:
                builder = self.B(self.priority, line_node)
                one_way: dict[str, Literal["forwards", "backwards"]] = {}
                platform_codes: dict[str, tuple[str | None, str | None]] = {}

                for station in route.stations:
                    matches = re.match(R"(?P<name>[^@#<>]+)\s*?(?:@(?P<code>[^@#<>]*)|)\s*?(?:#(?P<one_way>[^@#<>]*)|)\s*?(?:<(?P<forward_code>[^@#<>]*)\s*?>(?P<backward_code>[^@#<>]*)|)", station)
                    name = matches["name"].strip()
                    code = name if (c := matches["code"] is None) else c.strip()
                    if (direction := matches["one_way"]) is not None:
                        direction = direction.strip()
                        assert direction in ("forwards", "backwards")
                        one_way[name] = direction
                    if (forward_code := matches["forward_code"]) is not None and (backward_code := matches["backward_code"]) is not None:
                        forward_code, backward_code = forward_code.strip(), backward_code.strip()
                        forward_code = None if forward_code == "-" else forward_code
                        backward_code = None if backward_code == "-" else backward_code
                        platform_codes[name] = forward_code, backward_code
                    builder.add(self.S.create(
                        self.conn, self.priority,
                        codes={code},
                        name=name,
                        company=company,
                    ))
                self.routing(line_node, builder, line, route, one_way, platform_codes)

        for code, (x, z) in file.coords.items():
            self.S.create(
                self.conn, self.priority,
                codes={code},
                company=company,
                world=file.world,
                coordinates=(x, z),
            )

        for set_ in file.proximity:
            for code1, code2 in itertools.combinations(set_, 2):
                st1 = self.S.create(self.conn, self.priority, codes={code1}, company=company)
                st2 = self.S.create(self.conn, self.priority, codes={code2}, company=company)
                x1, y1 = file.coords[code1]
                x2, y2 = file.coords[code2]
                gt.Proximity.create(self.conn, (self.priority,), node1=st1, node2=st2, distance=((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5, explicit=True)

    def routing(
        self,
        line_node: gt.RailLine | gt.BusLine | gt.SeaLine,
        builder: RailLineBuilder | BusLineBuilder | SeaLineBuilder,
        line_yaml: YamlLine,
        route_yaml: YamlRoute,
        one_way: dict[str, Literal["forwards", "backwards"]] | None,
        platform_codes: dict[str, tuple[str | None, str | None]] | None,
    ):
        builder.connect(
            one_way=one_way, platform_codes=platform_codes,
            forward_direction=route_yaml.forward_direction,
            backward_direction=route_yaml.backward_direction,
        )


class BusYaml2Source(Yaml2Source, BusSource):
    C = gt.BusCompany
    L = gt.BusLine
    S = gt.BusStop
    P = gt.BusBerth
    B = BusLineBuilder


class RailYaml2Source(Yaml2Source, RailSource):
    C = gt.RailCompany
    L = gt.RailLine
    S = gt.RailStation
    P = gt.RailPlatform
    B = RailLineBuilder


class SeaYaml2Source(Yaml2Source, SeaSource):
    C = gt.SeaCompany
    L = gt.SeaLine
    S = gt.SeaStop
    P = gt.SeaDock
    B = SeaLineBuilder
