from __future__ import annotations

import uuid
from typing import Any, Self, TYPE_CHECKING, ClassVar

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
    sources: set[str] = msgspec.field(default_factory=set)

    def source(self, source: Sourced | Source) -> Self:
        if isinstance(source, Sourced):
            self.sources = self.sources.union(source.sources)
            return self
        if isinstance(source, Source):
            self.sources.add(source.name)
            return self
        raise NotImplementedError


    def dict(self) -> dict[str, Any]:
        return {
            'v': str(self.v.id) if isinstance(self.v, BaseObject) else self.v.dict(),
            'sources': self.sources
        }


class Source:
    name: ClassVar[str | None] = None
