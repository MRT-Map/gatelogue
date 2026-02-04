from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self

import gatelogue_types as gt

if TYPE_CHECKING:
    from gatelogue_types import (
        BusLine,
        BusStop,
        RailLine,
        RailStation,
        SeaLine,
        SeaStop,
    )

type _OneWay = Literal["forwards", "backwards"]


class LineBuilder[L: (BusLine, RailLine, SeaLine), S: (BusStop, RailStation, SeaStop)]:
    Pt: ClassVar[type[gt.BusBerth, gt.SeaDock, gt.RailPlatform]]
    Cn: ClassVar[type[gt.BusConnection, gt.SeaConnection, gt.RailConnection]]
    default_forward_code: ClassVar[str | None] = "forwards"
    default_backward_code: ClassVar[str | None] = "forwards"

    def __init__(self, src: int, line: L):
        self.src = src
        self.line = line

        self.station_list: list[S] = []
        self.cursor = 0
        self.prev_platform_forwards: type[LineBuilder.Pt] | None = None
        self.prev_platform_backwards: type[LineBuilder.Pt] | None = None

    def add(self, *stations: S):
        self.station_list.extend(stations)

    def connect_to(
        self,
        station: str | S,
        *,
        one_way: _OneWay | None = None,
        forward_code: str | None = "DEFAULT",
        backward_code: str | None = "DEFAULT",
        forward_direction: str | None = None,
        backward_direction: str | None = None,
        **_
    ):
        station = next(a for a in self.station_list if a.name == station) if isinstance(station, str) else station
        forward_direction = f"towards {station.name}" if forward_direction == "" else None
        backward_direction = f"towards {self.station_list[0].name}" if backward_direction == "" else None
        if forward_code == "DEFAULT":
            forward_code = self.default_forward_code
        elif forward_code == "LINE":
            forward_code = self.line.code
        if backward_code == "DEFAULT":
            backward_code = self.default_backward_code
        elif backward_code == "LINE":
            backward_code = self.line.code
        station_attr = "station" if issubclass(self.Pt, gt.RailPlatform) else "stop"

        if one_way != "backwards":
            platform_forwards = self.Pt.create(
                station.conn,
                self.src,
                code=forward_code,
                **{station_attr: station},
            )
            if self.prev_platform_forwards is not None and getattr(self.prev_platform_forwards, station_attr) != station:
                self.Cn.create(
                    station.conn,
                    self.src,
                    line=self.line,
                    from_=self.prev_platform_forwards,
                    to=platform_forwards,
                    direction=forward_direction,
                )
            self.prev_platform_forwards = platform_forwards
        if one_way != "forwards":
            platform_backwards = self.Pt.create(
                station.conn,
                self.src,
                code=backward_code,
                **{station_attr: station},
            )
            if self.prev_platform_backwards is not None and getattr(self.prev_platform_backwards, station_attr) != station:
                self.Cn.create(
                    station.conn,
                    self.src,
                    line=self.line,
                    from_=platform_backwards,
                    to=self.prev_platform_backwards,
                    direction=backward_direction,
                )
            self.prev_platform_backwards = platform_backwards

    def connect(
        self,
        *,
        until: str | None = None,
        until_before: str | None = None,
        one_way: dict[str, _OneWay] | None = None,
        platform_codes: dict[str, tuple[str | None, str | None]] | None = None,
        forward_direction: str | None = "",
        backward_direction: str | None = "",
    ):
        if self.cursor == len(self.station_list):
            return
        forward_direction = f"towards {self.station_list[-1].name}" if forward_direction == "" else None
        backward_direction = f"towards {self.station_list[0].name}" if backward_direction == "" else None
        one_way = one_way or {}
        platform_codes = platform_codes or {}

        while True:
            station = self.station_list[self.cursor]
            forward_code, backward_code = platform_codes.get(
                station.name, (self.default_forward_code, self.default_backward_code)
            )
            self.connect_to(
                station,
                one_way=one_way.get(station.name, one_way.get("*", None)),
                forward_code=forward_code,
                backward_code=backward_code,
                forward_direction=forward_direction,
                backward_direction=backward_direction,
            )

            self.cursor += 1
            if (
                self.cursor >= len(self.station_list)
                or self.station_list[self.cursor - 1].name == until
                or self.station_list[self.cursor].name == until_before
            ):
                break

    def connect_circle(
        self,
        *,
        one_way: dict[str, _OneWay] | None = None,
        platform_codes: dict[str, tuple[str | None, str | None]] | None = None,
        forward_direction: str | None = None,
        backward_direction: str | None = None,
    ):
        self.connect(
            one_way=one_way,
            platform_codes=platform_codes,
            forward_direction=forward_direction,
            backward_direction=backward_direction,
        )
        self.connect_to(
            self.station_list[0],
            one_way=one_way.get(self.station_list[0].name, one_way.get("*", None)) if one_way is not None else None,
            forward_direction=forward_direction,
            backward_direction=backward_direction,
        )

    def skip(self, *, until: str, detached: bool = False):
        while self.cursor < len(self.station_list) and self.station_list[self.cursor].name != until:
            self.cursor += 1
        if detached:
            self.prev_platform_forwards = None
            self.prev_platform_backwards = None

    def branch_off(self, *, terminus: str | None = None) -> Self:
        branch = self.copy()

        if terminus is not None:
            self.skip(until=terminus)
            self.cursor += 1
            branch.station_list = self.station_list[: self.cursor]

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

    def u_turn(self) -> Self:
        self.station_list = list(reversed(self.station_list))
        self.cursor = len(self.station_list) - 1 - self.cursor
        self.prev_platform_backwards, self.prev_platform_forwards = self.prev_platform_forwards, self.prev_platform_backwards
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
    default_forward_code = "LINE"
    default_backward_code = "LINE"
