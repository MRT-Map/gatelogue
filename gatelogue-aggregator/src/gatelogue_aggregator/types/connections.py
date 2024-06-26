from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, ClassVar, override

import msgspec

from gatelogue_aggregator.types.base import BaseContext, ToSerializable

if TYPE_CHECKING:
    import uuid
    from collections.abc import Callable

    from gatelogue_aggregator.types.node.base import Node


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Direction[CTX: BaseContext](ToSerializable):
    forward_towards_code: str
    forward_direction_label: str | None
    backward_direction_label: str | None
    one_way: bool = False

    @override
    class Ser(msgspec.Struct, kw_only=True):
        import uuid

        forward_towards_code: uuid.UUID
        """ID of the :py:class:`RailStation`/:py:class:`SeaStop`/:py:class:`BusStop` that the other fields take with respect to. Should be either of the stations/stops of the connection"""
        forward_direction_label: str | None
        """Describes the direction taken when travelling **towards the station/stop in** ``forward_towards_code``"""
        backward_direction_label: str | None
        """Describes the direction taken when travelling **from the station/stop in** ``forward_towards_code``"""
        one_way: bool
        """Whether the connection is one-way, ie. travel **towards the station/stop in** ``forward_towards_code`` is possible but not the other way"""


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Connection[CTX: BaseContext, C: Node, L: Node, S: Node](ToSerializable):
    CT: ClassVar[type[Node]]
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
        import uuid

        line: uuid.UUID
        """ID of the :py:class:`RailLine`/:py:class:`SeaLine`/:py:class:`BusLine` that the connection is made on"""
        direction: Direction.Ser | None = None
        """Direction information"""

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
            else type(self).station_fn(ctx)(codes={self.direction.forward_towards_code}, company=self.get_company(ctx)).id
        )

    def set_direction_forward_towards(self, ctx: CTX, v: S):
        self.direction.forward_towards_code = v.merged_attr(ctx, "codes")[0]
        self.set_company(ctx, v.get_one(ctx, self.CT))

    def get_line(self, ctx: CTX) -> L:
        return type(self).line_fn(ctx)(code=self.line_code, company=self.get_company(ctx))

    def set_line(self, ctx: CTX, v: L):
        self.line_code = v.merged_attr(ctx, "code")
        self.set_company(ctx, v.get_one(ctx, self.CT))


class Proximity(msgspec.Struct):
    distance: int
    """Distance between the two objects in blocks"""
