from __future__ import annotations

from typing import Generic, TypeVar

import gatelogue_types as gt
import msgspec

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.node.base import Node, NodeRef

L = TypeVar("L", bound=Node)
S = TypeVar("S", bound=Node)
CTX = TypeVar("CTX", bound=BaseContext)


class Direction(gt.Direction, msgspec.Struct, Generic[CTX, S]):
    direction: NodeRef[S]

    def get_direction(self, ctx: CTX) -> S:
        return ctx.find_by_ref_or_index(self.direction)

    def set_direction(self, ctx: CTX, v: S):
        self.direction = v.ref(ctx)

    def sanitise_strings(self):
        if self.forward_label is not None:
            self.forward_label = str(self.forward_label).strip()
        if self.backward_label is not None:
            self.backward_label = str(self.backward_label).strip()

    def export(self, ctx: CTX) -> gt.Direction:
        return gt.Direction(
            direction=self.get_direction(ctx).i,
            forward_label=self.forward_label,
            backward_label=self.backward_label,
            one_way=self.one_way,
        )


class Connection(gt.Connection, msgspec.Struct, Generic[CTX, L]):
    line: NodeRef
    direction: Direction | None = None

    def get_line(self, ctx: CTX) -> L:
        return ctx.find_by_ref_or_index(self.line)

    def set_line(self, ctx: CTX, v: L):
        self.line = v.ref(ctx)

    def sanitise_strings(self):
        if self.direction is not None:
            self.direction.sanitise_strings()

    def export(self, ctx: CTX) -> gt.Connection:
        return gt.Connection(
            line=self.get_line(ctx).i, direction=self.direction.export(ctx) if self.direction is not None else None
        )
