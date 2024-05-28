from typing import TypeAlias, TypeVar

import msgspec

T = TypeVar("T")


class SourceInner[T](msgspec.Struct):
    value: T
    sources: list[str]


Sourced: TypeAlias = T | SourceInner[T]()
