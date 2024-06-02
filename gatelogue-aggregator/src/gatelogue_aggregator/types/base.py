from __future__ import annotations

import dataclasses
import re
import uuid
from collections.abc import Generator
from typing import TYPE_CHECKING, Any, ClassVar, Self, override, TypeVar, Generic, AnyStr

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

    def ser(self) -> SerializableClass:  # noqa: F821
        pass


class MergeableObject:
    def equivalent(self, other: Self) -> bool:
        raise NotImplementedError

    def merge(self, ctx: BaseContext, other: Self):
        raise NotImplementedError

    def merge_if_equivalent(self, ctx: BaseContext, other: Self) -> bool:
        if self.equivalent(other):
            self.merge(ctx, other)
            return True
        return False

    @staticmethod
    def merge_lists[T: MergeableObject](ctx: BaseContext, self: list[T], other: list[T]):
        for o in other:
            for s in self:
                if s.merge_if_equivalent(ctx, o):
                    break
            else:
                self.append(o)


class IdObject(msgspec.Struct, MergeableObject, kw_only=True):
    id: ID = msgspec.field(default_factory=ID)

    def ctx(self, ctx: BaseContext):
        raise NotImplementedError

    def de_ctx(self, ctx: BaseContext):
        raise NotImplementedError

    def update(self, ctx: BaseContext):
        raise NotImplementedError

    def source(self, source: Sourced | Source) -> Sourced[Self]:
        return Sourced(self).source(source)


_T = TypeVar("_T")


class Sourced[T](msgspec.Struct, MergeableObject, ToSerializable):
    v: T
    s: set[str] = msgspec.field(default_factory=set)

    @override
    class SerializableClass(msgspec.Struct, Generic[_T]):
        v: _T
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

    def merge(self, ctx: BaseContext, other: Self):
        if isinstance(self.v, MergeableObject):
            self.v.merge(ctx, other.v)
        self.s.update(other.s)


class Source:
    name: ClassVar[str]

    def __init__(self):
        rich.print(f"[yellow]Retrieving from {self.name}")


class BaseContext(ToSerializable):
    pass


def search_all(regex: re.Pattern[str], text: str) -> Generator[re.Match[str], None, None]:
    pos = 0
    while (match := regex.search(text, pos)) is not None:
        pos = match.end()
        yield match


def process_code[T: (str, None)](s: T) -> T:
    if s is None:
        return None
    res = ""
    hyphen = False
    for match in search_all(re.compile(r"\d+|[A-Za-z]+|[^\dA-Za-z]+"), str(s).strip()):
        t = match.group(0)
        if len(t) == 0:
            continue
        if (hyphen and t[0].isdigit()) or (len(res) != 0 and t[0].isdigit() and res[-1].isdigit()):
            res += "-"
        if hyphen:
            hyphen = False
        if t.isdigit():
            res += t.lstrip("0") or "0"
        elif t.isalpha():
            res += t.upper()
        elif t == "-" and (len(res) == 0 or res[-1].isalpha()):
            hyphen = True

    return res


def process_airport_code[T: (str, None)](s: T) -> T:
    if s is None:
        return None
    s = str(s).upper()
    if len(s) == 4 and s[3] == "T":
        return s[:3]
    return s
