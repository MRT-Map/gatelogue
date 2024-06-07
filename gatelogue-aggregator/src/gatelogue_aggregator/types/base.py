from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, Self, TypeVar, override

import msgspec
import networkx as nx
import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT

if TYPE_CHECKING:
    from pathlib import Path

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


class Sourced[T](msgspec.Struct, Mergeable, ToSerializable):
    v: T
    s: set[str] = msgspec.field(default_factory=set)

    def __str__(self):
        s = str(self.v)
        if len(self.s) != 0:
            s += " (" + ", ".join(self.s) + ")"
        return s

    @override
    class Ser(msgspec.Struct, Generic[_T]):
        v: _T
        s: set[str]

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

    def __init__(self, _: Path = DEFAULT_CACHE_DIR, __: int = DEFAULT_TIMEOUT):
        rich.print(f"[yellow]Retrieving from {self.name}")
