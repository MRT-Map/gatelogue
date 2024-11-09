from __future__ import annotations

from typing import TYPE_CHECKING, Self

import rustworkx as rx


if TYPE_CHECKING:
    from gatelogue_aggregator.types.node.base import Node, NodeRef


class BaseContext:
    g: rx.PyGraph

    def __init__(self):
        self.g = rx.PyGraph()

    def find_by_ref[R: NodeRef, N: Node](self, v: R) -> N | None:
        indices = self.g.filter_nodes(lambda a: v.refs(self, a))
        if len(indices) == 0:
            return
        return self.g[indices[0]]

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    def find_by_ref_or_index[R: NodeRef, N: Node](self, v: R | int) -> N | None:
        from gatelogue_aggregator.types.node.base import NodeRef

        if isinstance(v, NodeRef):
            return self.find_by_ref(v)
        if isinstance(v, int):
            return self.g[v]
        raise TypeError(type(v))


class Mergeable[CTX: BaseContext]:
    def equivalent(self, ctx: CTX, other: Self) -> bool:
        raise NotImplementedError

    def merge(self, ctx: CTX, other: Self):
        raise NotImplementedError

    def merge_if_equivalent(self, ctx: CTX, other: Self) -> bool:
        if self.equivalent(ctx, other):
            self.merge(ctx, other)
            return True
        return False

    @staticmethod
    def merge_lists[T: Mergeable](ctx: CTX, self: list[T], other: list[T]):
        for o in other:
            for s in self:
                if s.merge_if_equivalent(ctx, o):
                    break
            else:
                self.append(o)
