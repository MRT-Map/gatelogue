from __future__ import annotations

import dataclasses
import itertools
import uuid
from collections.abc import Callable
from typing import override, ClassVar, TypeAlias

import msgspec

from gatelogue_aggregator.types.base import ToSerializable, BaseContext
from gatelogue_aggregator.types.connections import Direction, Connection
from gatelogue_aggregator.types.node.base import Node


class LineBuilder[CTX: BaseContext]:
    L: ClassVar[type[Node]]
    S: ClassVar[type[Node]]
    Conn: ClassVar[type[Connection]]

    def __init__(self, ctx: CTX, line: L):
        self.ctx = ctx
        self.line = line

    def connect(
        self,
        *stations: S,
        forward_label: str | None = None,
        backward_label: str | None = None,
        one_way: bool = False,
    ):
        if len(stations) == 0:
            return
        self.line.connect_one(self.ctx, stations[0])
        forward_label = forward_label or "towards " + (
            a.v
            if (a := stations[-1].merged_attr(self.ctx, "name")) is not None
            else next(iter(stations[-1].merged_attr(self.ctx, "codes")))
        )
        backward_label = backward_label or "towards " + (
            a.v
            if (a := stations[0].merged_attr(self.ctx, "name")) is not None
            else next(iter(stations[0].merged_attr(self.ctx, "codes")))
        )
        for s1, s2 in itertools.pairwise(stations):
            s1.connect(
                self.ctx,
                s2,
                value=type(self).Conn(
                    self.ctx,
                    line=self.line,
                    direction=Direction(
                        forward_towards_code=next(iter(s2.merged_attr(self.ctx, "codes", set))),
                        forward_direction_label=forward_label,
                        backward_direction_label=backward_label,
                        one_way=one_way,
                    ),
                ),
            )

    def circle(
        self,
        *stations: S,
        forward_label: str | None = None,
        backward_label: str | None = None,
        one_way: bool = False,
    ):
        if len(stations) == 0:
            return
        self.connect(
            *stations, stations[0], forward_label=forward_label, backward_label=backward_label, one_way=one_way
        )
