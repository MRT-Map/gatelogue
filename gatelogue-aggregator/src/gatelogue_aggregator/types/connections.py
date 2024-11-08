from __future__ import annotations

import dataclasses
import functools
from struct import Struct
from typing import TYPE_CHECKING, ClassVar, override, Callable, Any

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Sourced

if TYPE_CHECKING:
    import uuid
    from collections.abc import Callable

    from gatelogue_aggregator.types.node.base import Node, NodeRef


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Direction[CTX: BaseContext, S: Node](msgspec.Struct):
    direction: NodeRef | int
    """Reference to or ID of the station/stop that the other fields take with respect to. Should be either node of the connection"""
    forward_label: str | None
    """Describes the direction taken when travelling **towards the station/stop in** ``forward_towards_code``"""
    backward_label: str | None
    """Describes the direction taken when travelling **from the station/stop in** ``forward_towards_code``"""
    one_way: bool | Sourced[bool] = False
    """Whether the connection is one-way, ie. travel **towards the station/stop in** ``forward_towards_code`` is possible but not the other way"""

    @property
    def direction_node(self) -> Callable[[CTX], S]:
        return lambda ctx: ctx.find_by_ref_or_index(self.direction)

    @direction_node.setter
    def direction_node(self, v: S):
        self.direction = v.ref()


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Connection[CTX: BaseContext, L: Node](msgspec.Struct):
    line: NodeRef | int
    """Reference to or ID of the line that the connection is made on"""
    direction: Direction | None = None
    """Direction information"""

    @property
    def line_node(self) -> Callable[[CTX], L]:
        return lambda ctx: ctx.find_by_ref_or_index(self.line)

    @line_node.setter
    def line_node(self, v: L):
        self.line = v.ref()


class Proximity(msgspec.Struct):
    distance: int
    """Distance between the two objects in blocks"""
