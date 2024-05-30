from __future__ import annotations

import abc
import uuid
from typing import TYPE_CHECKING, Any, ClassVar, Self, override

import msgspec
import rich

if TYPE_CHECKING:
    from gatelogue_aggregator.types.context import Context


class ID(msgspec.Struct, kw_only=True):
    id: uuid.UUID | ID = msgspec.field(default_factory=uuid.uuid4)

    def __str__(self):
        if isinstance(self, ID):
            return str(self.id)
        return self.id.hex

    def __eq__(self, other):
        if isinstance(other, ID):
            return str(self) == str(other)
        return False


class ToSerializable:
    SerializableClass: ClassVar[type]

    def ser(self) -> SerializableClass:
        pass


class MergeableObject:
    def equivalent(self, other: Self) -> bool:
        raise NotImplementedError

    def merge(self, other: Self):
        raise NotImplementedError

    def merge_if_equivalent(self, other: Self) -> bool:
        if self.equivalent(other):
            self.merge(other)
            return True
        return False

    @staticmethod
    def merge_lists[T: MergeableObject](self: list[T], other: list[T]):
        for o in other:
            for s in self:
                if s.merge_if_equivalent(o):
                    break
            else:
                self.append(o)


class IdObject(msgspec.Struct, MergeableObject, kw_only=True):
    id: ID = msgspec.field(default_factory=ID)

    def ctx(self, ctx: Context):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def source(self, source: Sourced | Source) -> Sourced[Self]:
        return Sourced(self).source(source)


class Sourced[T](msgspec.Struct, MergeableObject, ToSerializable):
    v: T
    s: set[str] = msgspec.field(default_factory=set)

    @override
    class SerializableClass(msgspec.Struct):
        v: Any
        s: set[str]

    @override
    def ser(self) -> SerializableClass:
        return self.SerializableClass(
            v=str(self.v.id) if isinstance(self.v, IdObject) else self.v.ser() if hasattr(self.v, "ser") else self.v,
            s=self.s,
        )

    def source(self, source: Sourced | Source) -> Self:
        if isinstance(source, Sourced):
            self.s.update(source.s)
            return self
        if isinstance(source, Source):
            self.s.add(source.name)
            return self
        raise NotImplementedError

    def equivalent(self, other: Self) -> bool:
        return self.v.equivalent(other.v) if isinstance(self.v, MergeableObject) else self.v == other.v

    def merge(self, other: Self):
        if isinstance(self.v, MergeableObject):
            self.v.merge(other.v)
        self.s.update(other.s)


class Source:
    name: ClassVar[str]

    def __init__(self):
        rich.print(f"[yellow]Retrieving from {self.name}")
