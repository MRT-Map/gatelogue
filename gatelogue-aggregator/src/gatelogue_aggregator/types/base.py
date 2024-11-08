from __future__ import annotations

import functools
import pickle
from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar, Generic, Self, TypeVar, override

import msgspec
import rustworkx as rx
import rich

from gatelogue_aggregator.logging import ERROR, INFO1

if TYPE_CHECKING:
    from gatelogue_aggregator.types.config import Config
    from gatelogue_aggregator.types.node.base import Node, NodeRef


class BaseContext:
    g: rx.PyGraph

    def __init__(self):
        self.g = rx.PyGraph()

    def find_by_ref[R: NodeRef, N: Node](self, v: R) -> N | None:
        indices = self.g.filter_nodes(lambda a: v.refs(a))
        if len(indices) == 0:
            return
        return self.g[indices[0]]

    def find_by_ref_or_index[R: NodeRef, N: Node](self, v: R | int) -> N | None:
        if isinstance(v, NodeRef):
            return self.find_by_ref(v)
        if isinstance(v, int):
            return self.g[v]
        raise TypeError(type(v))


class Mergeable[CTX: BaseContext]:
    def equivalent(self, other: Self) -> bool:
        raise NotImplementedError

    def merge(self, ctx: CTX, other: Self):
        raise NotImplementedError

    def merge_if_equivalent(self, ctx: CTX, other: Self) -> bool:
        if self.equivalent(other):
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


class Sourced[T](msgspec.Struct, Mergeable):
    v: T
    """Actual value"""
    s: set[type[Source]] = msgspec.field(default_factory=set)
    """List of sources that support the value"""

    def __str__(self):
        s = str(self.v)
        if len(self.s) != 0:
            s += " (" + ", ".join(self.s) + ")"
        return s

    def source(self, source: Sourced | Source | type[Source]) -> Self:
        if isinstance(source, Sourced):
            self.s.update(source.s)
            return self
        if isinstance(source, Source) or (isinstance(source, type) and issubclass(source, Source)):
            self.s.add(source)
            return self
        raise NotImplementedError(self)

    def equivalent(self, other: Self) -> bool:
        return self.v.equivalent(other.v) if isinstance(self.v, Mergeable) else self.v == other.v

    def merge(self, ctx: BaseContext, other: Self):
        if self.v == other.v:
            self.source(other)
            return
        if isinstance(self.v, set) and isinstance(other.v, set):
            self.v.update(other.v)
            self.s.update(other.s)
            return
        if isinstance(self.v, Mergeable):
            if self.v.merge_if_equivalent(ctx, other.v):
                self.s.update(other.s)
                return
        # TODO add to discrepancy list
        if max(self.s, key=lambda x: x.priority) < max(other.s, key=lambda x: x.priority):
            self.v = other.v
            self.s = other.s


class SourceMeta(type):
    name: str
    priority: float | int

    def __lt__(cls, other):
        return cls.priority < other.priority

    def __str__(self):
        return self.name

    def encode(cls, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return cls.name.encode(encoding, errors)


class Source(metaclass=SourceMeta):
    name: ClassVar[str]
    priority: ClassVar[float | int]

    def __init__(self, _: Config):
        rich.print(INFO1 + f"Retrieving from {self.name}")

    @classmethod
    def retrieve_from_cache(cls, config: Config) -> rx.PyGraph | None:
        if cls.__name__ in config.cache_exclude:
            return None
        cache_file = config.cache_dir / "network-cache" / cls.__name__
        if not cache_file.exists():
            return None
        rich.print(INFO1 + f"Retrieving from cache {cache_file}")
        return pickle.loads(cache_file.read_bytes(), encoding="utf-8")  # noqa: S301

    @classmethod
    def save_to_cache(cls, config: Config, g: rx.PyGraph):
        if g.num_nodes() == 0:
            rich.print(ERROR + f"{cls.__name__} yielded no results")

        cache_file = config.cache_dir / "network-cache" / cls.__name__
        rich.print(INFO1 + f"Saving to cache {cache_file}")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.touch()
        cache_file.write_bytes(pickle.dumps(g))
