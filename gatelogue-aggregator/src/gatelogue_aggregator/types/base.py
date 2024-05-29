from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, ClassVar, Self

import msgspec

if TYPE_CHECKING:
    from gatelogue_aggregator.types.context import Context


class ID(msgspec.Struct, kw_only=True):
    id: uuid.UUID = msgspec.field(default_factory=uuid.uuid4)

    def __str__(self):
        return self.id.hex


class BaseObject(msgspec.Struct, kw_only=True):
    id: ID = msgspec.field(default_factory=ID)

    def ctx(self, ctx: Context):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class Sourced[T](msgspec.Struct):
    v: T
    s: set[str] = msgspec.field(default_factory=set)

    def source(self, source: Sourced | Source) -> Self:
        if isinstance(source, Sourced):
            self.s = self.s.union(source.s)
            return self
        if isinstance(source, Source):
            self.s.add(source.name)
            return self
        raise NotImplementedError

    def dict(self) -> dict[str, Any]:
        return {"v": str(self.v.id) if isinstance(self.v, BaseObject) else self.v.dict() if hasattr(self.v, "dict") else self.v, "sources": self.s}


class Source:
    name: ClassVar[str | None] = None
