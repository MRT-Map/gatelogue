from __future__ import annotations

import pickle
from typing import TYPE_CHECKING, ClassVar, Generic, Self, TypeVar, override

import msgspec
import networkx as nx
import rich

from gatelogue_aggregator.logging import INFO1

if TYPE_CHECKING:
    from gatelogue_aggregator.types.config import Config
    from gatelogue_aggregator.types.node.base import Node


class ToSerializable:
    class Ser(msgspec.Struct, kw_only=True):
        pass

    def ser(self, ctx: BaseContext) -> Node.Ser:
        raise NotImplementedError


class BaseContext(ToSerializable):
    g: nx.MultiGraph

    def __init__(self):
        self.g = nx.MultiGraph()


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


_T = TypeVar("_T")


class Sourced(msgspec.Struct, Mergeable, ToSerializable, Generic[_T]):
    v: _T
    s: set[str] = msgspec.field(default_factory=set)

    def __str__(self):
        s = str(self.v)
        if len(self.s) != 0:
            s += " (" + ", ".join(self.s) + ")"
        return s

    @override
    class Ser(msgspec.Struct, Generic[_T]):
        v: _T
        """Actual value"""
        s: set[str]
        """List of sources that support the value"""

    def ser(self, ctx: BaseContext) -> Ser:
        from gatelogue_aggregator.types.node.base import Node

        return self.Ser(
            v=str(self.v.id)
            if isinstance(self.v, Node)
            else self.v.ser(ctx)
            if isinstance(self.v, ToSerializable)
            else self.v,
            s=self.s,
        )

    def source(self, source: Sourced | Source | type[Source]) -> Self:
        if isinstance(source, Sourced):
            self.s.update(source.s)
            return self
        if isinstance(source, Source) or (isinstance(source, type) and issubclass(source, Source)):
            self.s.add(source.name)
            return self
        raise NotImplementedError(self)

    def equivalent(self, ctx: BaseContext, other: Self) -> bool:
        return self.v.equivalent(ctx, other.v) if isinstance(self.v, Mergeable) else self.v == other.v

    def merge(self, ctx: BaseContext, other: Self):
        if isinstance(self.v, Mergeable):
            self.v.merge(ctx, other.v)
        self.s.update(other.s)


class SourceMeta(type):
    name: str
    priority: float | int

    def __lt__(cls, other):
        return cls.priority < other.priority

    def encode(cls, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return cls.name.encode(encoding, errors)


class Source(metaclass=SourceMeta):
    name: ClassVar[str]
    priority: ClassVar[float | int]

    def __init__(self, _: Config):
        rich.print(INFO1 + f"Retrieving from {self.name}")

    @classmethod
    def retrieve_from_cache(cls, config: Config) -> nx.MultiGraph | None:
        if cls.__name__ in config.cache_exclude:
            return None
        cache_file = config.cache_dir / "network-cache" / cls.__name__
        if not cache_file.exists():
            return None
        rich.print(INFO1 + f"Retrieving from cache {cache_file}")
        return pickle.loads(cache_file.read_bytes(), encoding="utf-8")  # noqa: S301

    @classmethod
    def save_to_cache(cls, config: Config, g: nx.MultiGraph):
        cache_file = config.cache_dir / "network-cache" / cls.__name__
        rich.print(INFO1 + f"Saving to cache {cache_file}")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.touch()
        cache_file.write_bytes(pickle.dumps(g))
