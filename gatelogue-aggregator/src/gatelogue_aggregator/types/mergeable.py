from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from gatelogue_aggregator.types.source import Source


class Mergeable:
    def equivalent(self, src: Source, other: Self) -> bool:
        raise NotImplementedError

    def merge(self, src: Source, other: Self):
        raise NotImplementedError

    def merge_if_equivalent(self, src: Source, other: Self) -> bool:
        if self.equivalent(src, other):
            self.merge(src, other)
            return True
        return False

    @staticmethod
    def merge_lists[T: Mergeable](src: Source, self: list[T], other: list[T]):
        for o in other:
            for s in self:
                if s.merge_if_equivalent(src, o):
                    break
            else:
                self.append(o)
