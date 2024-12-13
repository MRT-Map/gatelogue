from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, ClassVar

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.connections import Connection, Direction

if TYPE_CHECKING:
    from collections.abc import Container

    from gatelogue_aggregator.types.node.base import Node


class LineBuilder[CTX: BaseContext, L: Node, S: Node]:
    CnT: ClassVar[type[Connection]]

    def __init__(self, ctx: CTX, line: L):
        self.ctx = ctx
        self.line = line

    def connect(
        self,
        *stations: S,
        forward_label: str | None = None,
        backward_label: str | None = None,
        one_way: bool = False,
        between: tuple[str | None, str | None] | None = None,
        exclude: Container[str] | None = None,
    ):
        if len(stations) == 0:
            return
        for s in stations:
            s.sanitise_strings()
        if between is not None:
            i1 = i2 = None
            if between[0] is None:
                i1 = 0
            if between[1] is None:
                i2 = len(stations) - 1
            for i, s in enumerate(stations):
                if between[0] is not None and s.name.v == between[0]:
                    i1 = i
                if between[1] is not None and s.name.v == between[1]:
                    i2 = i
            if i1 is None:
                msg = f"{between[0]} not found in list {[s.name.v for s in stations]}"
                raise ValueError(msg)
            if i2 is None:
                msg = f"{between[1]} not found in list {[s.name.v for s in stations]}"
                raise ValueError(msg)
            stations = list(stations)[i1 : i2 + 1]
        if exclude is not None:
            stations = [s for s in stations if s.name.v not in exclude]

        self.line.connect_one(self.ctx, stations[0])
        forward_label = forward_label or "towards " + (
            a.v if (a := stations[-1].name) is not None else next(iter(stations[-1].codes))
        )
        backward_label = backward_label or "towards " + (
            a.v if (a := stations[0].name) is not None else next(iter(stations[0].codes))
        )
        for s1, s2 in itertools.pairwise(stations):
            s1.connect(
                self.ctx,
                s2,
                value=type(self).CnT(
                    line=self.line.ref(self.ctx),
                    direction=Direction(
                        direction=s2.ref(self.ctx),
                        forward_label=forward_label,
                        backward_label=backward_label,
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
        exclude: list[str] | None = None,
    ):
        if len(stations) == 0:
            return
        self.connect(
            *stations,
            stations[0],
            forward_label=forward_label,
            backward_label=backward_label,
            one_way=one_way,
            exclude=exclude,
        )

    def matrix(self, *stations: S):
        if len(stations) == 0:
            return
        self.line.connect_one(self.ctx, stations[0])
        for s1, s2 in itertools.combinations(stations, 2):
            forward_label = "towards " + (a.v if (a := s2.name) is not None else next(iter(s2.codes)))
            backward_label = "towards " + (a.v if (a := s1.name) is not None else next(iter(s1.codes)))
            s1.connect(
                self.ctx,
                s2,
                value=type(self).CnT(
                    line=self.line.ref(self.ctx),
                    direction=Direction(
                        direction=s2.ref(self.ctx),
                        forward_label=forward_label,
                        backward_label=backward_label,
                    ),
                ),
            )
