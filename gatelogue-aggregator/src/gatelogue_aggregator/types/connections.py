from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

if TYPE_CHECKING:
    from gatelogue_aggregator.types.base import BaseContext
    from gatelogue_aggregator.types.node.base import Node
    from gatelogue_aggregator.types.source import Sourced


class Direction[CTX: BaseContext, S: Node](msgspec.Struct):
    from gatelogue_aggregator.types.node.base import NodeRef

    direction: NodeRef[S] | int
    """Reference to or ID of the station/stop that the other fields take with respect to. Should be either node of the connection"""
    forward_label: str | None
    """Describes the direction taken when travelling **towards the station/stop in** ``forward_towards_code``"""
    backward_label: str | None
    """Describes the direction taken when travelling **from the station/stop in** ``forward_towards_code``"""
    one_way: bool | Sourced[bool] = False
    """Whether the connection is one-way, ie. travel **towards the station/stop in** ``forward_towards_code`` is possible but not the other way"""

    def get_direction(self, ctx: CTX) -> S:
        return ctx.find_by_ref_or_index(self.direction)

    def set_direction(self, ctx: CTX, v: S):
        self.direction = v.ref(ctx)

    def prepare_merge(self):
        if self.forward_label is not None:
            self.forward_label = str(self.forward_label).strip()
        if self.backward_label is not None:
            self.backward_label = str(self.backward_label).strip()


class Connection[CTX: BaseContext, L: Node](msgspec.Struct):
    from gatelogue_aggregator.types.node.base import NodeRef

    line: NodeRef[L] | int
    """Reference to or ID of the line that the connection is made on"""
    direction: Direction | None = None
    """Direction information"""

    def get_line(self, ctx: CTX) -> L:
        return ctx.find_by_ref_or_index(self.line)

    def set_line(self, ctx: CTX, v: L):
        self.line = v.ref(ctx)

    def prepare_merge(self):
        if self.direction is not None:
            self.direction.prepare_merge()

    def prepare_export(self, ctx: CTX):
        self.line = self.get_line(ctx).i
        if self.direction is not None:
            self.direction.direction = self.direction.get_direction(ctx).i
