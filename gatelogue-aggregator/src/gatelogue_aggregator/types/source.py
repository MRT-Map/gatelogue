from __future__ import annotations

import pickle
from typing import TYPE_CHECKING, ClassVar, Self

import msgspec
import rich

from gatelogue_aggregator.logging import ERROR, INFO1
from gatelogue_aggregator.types.base import BaseContext, Mergeable

if TYPE_CHECKING:
    import rustworkx as rx

    from gatelogue_aggregator.types.config import Config


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

    def equivalent(self, ctx: BaseContext, other: Self) -> bool:
        return self.v.equivalent(ctx, other.v) if isinstance(self.v, Mergeable) else self.v == other.v

    def merge(self, ctx: BaseContext, other: Self):
        if self.v == other.v:
            self.source(other)
            return
        if isinstance(self.v, set) and isinstance(other.v, set):
            self.v.update(other.v)
            self.s.update(other.s)
            return
        if isinstance(self.v, Mergeable) and self.v.merge_if_equivalent(ctx, other.v):
            self.s.update(other.s)
            return
        # TODO: add to discrepancy list
        if max(self.s, key=lambda x: x.priority) < max(other.s, key=lambda x: x.priority):
            self.v = other.v
            self.s = other.s


class SourceMeta(type):
    name: str
    priority: float | int

    def __lt__(cls, other):
        return cls.priority < other.priority

    def __str__(cls):
        return cls.name

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

    @classmethod
    def source[T](cls, v: T) -> Sourced[T]:
        return Sourced(v, s={cls})
