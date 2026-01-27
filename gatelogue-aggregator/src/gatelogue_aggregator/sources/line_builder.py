from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, ClassVar, Literal, Self

import gatelogue_types as gt

if TYPE_CHECKING:
    from collections.abc import Container
    from gatelogue_types import BusLine, RailLine, SeaLine, BusStop, RailStation, SeaStop, BusConnection, RailConnection, \
    SeaConnection, BusBerth, SeaDock, RailPlatform

type _OneWay = Literal["forwards", "backwards"]

class LineBuilder[L: (BusLine, RailLine, SeaLine), S: (BusStop, RailStation, SeaStop)]:
    Pt: ClassVar[type[gt.BusBerth, gt.SeaDock, gt.RailPlatform]]
    Cn: ClassVar[type[gt.BusConnection, gt.SeaConnection, gt.RailConnection]]

    def __init__(self, src: int, line: L):
        self.src = src
        self.line = line

        self.station_list: list[S] = []
        self.cursor = 0
        self.prev_platform_forwards: type[LineBuilder.Pt] | None = None
        self.prev_platform_backwards: type[LineBuilder.Pt] | None = None

    def add(self, *stations: S):
        self.station_list.extend(stations)

    def connect_to(self, station: str | S, *, one_way: _OneWay | None = None, forward_code: str | None = "forward", backward_code: str | None = "backwards", forward_direction: str | None = None, backward_direction: str | None = None,):
        station = next(a for a in self.station_list if a.name == station) if isinstance(station, str) else station

        if one_way != "backwards":
            platform_forwards = self.Pt.create(station.conn, self.src, code=forward_code, **{("station" if isinstance(self.Pt, gt.RailPlatform) else "stop"): station})
            if self.prev_platform_forwards is not None:
                self.Cn.create(station.conn, self.src, line=self.line, from_=self.prev_platform_forwards, to=platform_forwards, direction=forward_direction)
            self.prev_platform_forwards = platform_forwards
        if one_way != "forwards":
            platform_backwards = self.Pt.create(station.conn, self.src, code=backward_code, **{("station" if isinstance(self.Pt, gt.RailPlatform) else "stop"): station})
            if self.prev_platform_backwards is not None:
                self.Cn.create(station.conn, self.src, line=self.line, from_=platform_backwards, to=self.prev_platform_backwards, direction=backward_direction)
            self.prev_platform_backwards = platform_backwards

    def connect(self, *, until: str | None = None, until_before: str | None = None, one_way: dict[str, _OneWay] | None = None, platform_codes: dict[str, tuple[str | None, str | None]] | None = None, forward_direction: str | None = None, backward_direction: str | None = None,):
        forward_direction = forward_direction or f"towards {self.station_list[-1].name}"
        backward_direction = backward_direction or f"towards {self.station_list[0].name}"
        one_way = one_way or {}
        platform_codes = platform_codes or {}

        while True:
            station = self.station_list[self.cursor]
            forward_code, backward_code = platform_codes.get(station.name, ("forwards", "backwards"))
            self.connect_to(station, one_way=one_way.get(station.name, None), forward_code=forward_code, backward_code=backward_code, forward_direction=forward_direction, backward_direction=backward_direction)

            self.cursor += 1
            if self.cursor >= len(self.station_list) or self.station_list[self.cursor - 1].name == until or self.station_list[self.cursor].name == until_before:
                break

    def connect_circle(self, *, one_way: dict[str, _OneWay] | None = None, platform_codes: dict[str, tuple[str | None, str | None]] | None = None, forward_direction: str | None = None, backward_direction: str | None = None,):
        self.connect(one_way=one_way, platform_codes=platform_codes, forward_direction=forward_direction, backward_direction=backward_direction)
        self.connect_to(self.station_list[0], one_way=one_way, forward_direction=forward_direction, backward_direction=backward_direction)

    def skip(self, *, until: str):
        while self.cursor < len(self.station_list) and self.station_list[self.cursor].name != until:
            self.cursor += 1

    def branch_off(self, *, terminus: str | None = None) -> Self:
        branch = self.copy()

        if terminus is not None:
            self.skip(until=terminus)
            self.cursor += 1
            branch.station_list = self.station_list[:self.cursor]

        return branch

    def branch_detached(self, *, join_back_at: str | None = None) -> Self:
        branch = self.copy()
        branch.prev_platform_forwards = branch.prev_platform_backwards = None
        if join_back_at is not None:
            self.skip(until=join_back_at)
        return branch

    def copy(self) -> Self:
        branch = type(self)(self.src, self.line)
        branch.cursor = self.cursor
        branch.station_list = self.station_list
        branch.prev_platform_forwards = self.prev_platform_forwards
        branch.prev_platform_backwards = self.prev_platform_backwards
        return self


class BusLineBuilder(LineBuilder[gt.BusLine, gt.BusStop]):
    Pt = gt.BusBerth
    Cn = gt.BusConnection


class RailLineBuilder(LineBuilder[gt.RailLine, gt.RailStation]):
    Pt = gt.RailPlatform
    Cn = gt.RailConnection


class SeaLineBuilder(LineBuilder[gt.SeaLine, gt.SeaStop]):
    Pt = gt.SeaDock
    Cn = gt.SeaConnection
