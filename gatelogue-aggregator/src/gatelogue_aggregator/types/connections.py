from __future__ import annotations

import dataclasses
import uuid
from collections.abc import Callable
from typing import override, ClassVar, TypeAlias

import msgspec

from gatelogue_aggregator.types.base import ToSerializable, BaseContext
from gatelogue_aggregator.types.node.base import Node


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Direction[CTX: BaseContext](ToSerializable):
    forward_towards_code: str
    forward_direction_label: str | None
    backward_direction_label: str | None
    one_way: bool = False

    @override
    class Ser(msgspec.Struct, kw_only=True):
        forward_towards_code: uuid.UUID
        forward_direction_label: str | None
        backward_direction_label: str | None
        one_way: bool


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Connection[CTX: BaseContext](ToSerializable):
    C: ClassVar[type[Node]]
    L: ClassVar[type[Node]]
    S: ClassVar[type[Node]]
    company_fn: ClassVar[Callable[[CTX], Callable]]
    line_fn: ClassVar[Callable[[CTX], Callable]]
    station_fn: ClassVar[Callable[[CTX], Callable]]

    company_name: str
    line_code: str
    direction: Direction | None = None

    def __init__(self, ctx: CTX, *, line: L, direction: Direction | None = None):
        self.set_line(ctx, line)
        self.direction = direction

    @override
    class Ser(msgspec.Struct, kw_only=True):
        line: uuid.UUID
        direction: Direction.Ser | None = None

    def ser(self, ctx: CTX) -> Connection.Ser:
        return self.Ser(
            line=self.get_line(ctx).id,
            direction=Direction.Ser(
                forward_towards_code=self.get_direction_forward_towards(ctx),
                forward_direction_label=self.direction.forward_direction_label,
                backward_direction_label=self.direction.backward_direction_label,
                one_way=self.direction.one_way,
            )
            if self.direction is not None
            else None,
        )

    def get_company(self, ctx: CTX) -> C:
        return type(self).company_fn(ctx)(name=self.company_name)

    def set_company(self, ctx: CTX, v: C):
        self.company_name = v.merged_attr(ctx, "name")

    def get_direction_forward_towards(self, ctx: CTX) -> S | None:
        return (
            None
            if self.direction is None
            else type(self).station_fn(ctx)(codes={self.direction.forward_towards_code}, company=self.get_company(ctx))
        )

    def set_direction_forward_towards(self, ctx: CTX, v: S):
        self.direction.forward_towards_code = v.merged_attr(ctx, "codes")[0]
        self.set_company(ctx, v.get_one(ctx, self.C))

    def get_line(self, ctx: CTX) -> L:
        return type(self).line_fn(ctx)(code=self.line_code, company=self.get_company(ctx))

    def set_line(self, ctx: CTX, v: L):
        self.line_code = v.merged_attr(ctx, "code")
        self.set_company(ctx, v.get_one(ctx, self.C))


class Proximity(msgspec.Struct, kw_only=True):
    pass
