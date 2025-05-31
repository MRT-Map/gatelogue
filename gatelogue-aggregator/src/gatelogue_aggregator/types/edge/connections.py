from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

import gatelogue_types as gt
import msgspec

from gatelogue_aggregator.types.node.base import Node, NodeRef

if TYPE_CHECKING:
    from gatelogue_aggregator.types.source import Source

L = TypeVar("L", bound=Node)
S = TypeVar("S", bound=Node)


class Direction(gt.Direction, msgspec.Struct, Generic[S]):
    direction: NodeRef[S]

    def get_direction(self, src: Source) -> S:
        return src.find_by_ref_or_index(self.direction)

    def set_direction(self, src: Source, v: S):
        self.direction = v.ref(src)

    def sanitise_strings(self):
        if self.forward_label is not None:
            self.forward_label = str(self.forward_label).strip()
        if self.backward_label is not None:
            self.backward_label = str(self.backward_label).strip()

    def export(self, src: Source) -> gt.Direction:
        return gt.Direction(
            direction=self.get_direction(src).i,
            forward_label=self.forward_label,
            backward_label=self.backward_label,
            one_way=self.one_way,
        )


class Connection(gt.Connection, msgspec.Struct, Generic[L]):
    line: NodeRef
    direction: Direction | None = None

    def get_line(self, src: Source) -> L:
        return src.find_by_ref_or_index(self.line)

    def set_line(self, src: Source, v: L):
        self.line = v.ref(src)

    def sanitise_strings(self):
        if self.direction is not None:
            self.direction.sanitise_strings()

    def export(self, src: Source) -> gt.Connection:
        return gt.Connection(
            line=self.get_line(src).i, direction=self.direction.export(src) if self.direction is not None else None
        )
