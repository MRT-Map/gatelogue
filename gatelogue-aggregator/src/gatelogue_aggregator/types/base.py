from __future__ import annotations

import functools
import uuid
from typing import TypedDict, ClassVar, Type

import msgspec



class ID(msgspec.Struct, kw_only=True):
    id: uuid.UUID = msgspec.field(default_factory=uuid.uuid4)


class BaseObject(msgspec.Struct, kw_only=True):
    id: ID = msgspec.field(default_factory=ID)

class Sourced[T](msgspec.Struct):
    v: T
    sources: list[str] = []