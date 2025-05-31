from __future__ import annotations

import pickle
from typing import TYPE_CHECKING, ClassVar, Generic, Self, TypeVar

import gatelogue_types as gt
import msgspec
import rich
import rustworkx as rx

from gatelogue_aggregator.logging import ERROR, INFO1
from gatelogue_aggregator.sources import SOURCES
from gatelogue_aggregator.types.mergeable import Mergeable

if TYPE_CHECKING:
    from gatelogue_aggregator.types.config import Config
    from gatelogue_aggregator.types.node.base import Node, NodeRef

T = TypeVar("T")


class Sourced(gt.Sourced, msgspec.Struct, Mergeable, Generic[T]):
    def __str__(self):
        s = str(self.v)
        if len(self.s) != 0:
            s += " (" + ", ".join(str(a) for a in self.s) + ")"
        return s

    def source(self, source: Sourced | Source | type[Source]) -> Self:
        if isinstance(source, Sourced):
            self.s.update(source.s)
            return self
        if isinstance(source, Source):
            self.s.add(type(source).name)
            return self
        if isinstance(source, type) and issubclass(source, Source):
            self.s.add(source.name)
            return self
        raise NotImplementedError(source)

    def equivalent(self, src: Source, other: Self) -> bool:
        return self.v.equivalent(src, other.v) if isinstance(self.v, Mergeable) else self.v == other.v

    def merge(self, src: Source, other: Self, log_src: tuple[Node, str] | None = None):
        if self.v == other.v:
            self.source(other)
            return
        if isinstance(self.v, set) and isinstance(other.v, set):
            self.v.update(other.v)
            self.s.update(other.s)
            return
        if isinstance(self.v, Mergeable) and self.v.merge_if_equivalent(src, other.v):
            self.s.update(other.s)
            return

        def key(x):
            return next(a for a in SOURCES() if a.name == x).priority

        def log(outdated: Self, new: Self):
            if isinstance(log_src[0], gt.LocatedNode) and log_src[1] == "coordinates":
                return

            log_src_str = (
                "" if log_src is None else f"{type(log_src[0]).__name__} {log_src[0].str_src(src)}: attr {log_src[1]}: "
            )
            rich.print(
                ERROR
                + log_src_str
                + f"{', '.join(outdated.s)} reported outdated data {outdated.v}. {', '.join(new.s)} has updated data {new.v}"
            )

        if max(self.s, key=key) < max(other.s, key=key):
            log(self, other)
            self.v = other.v
            self.s = other.s
        else:
            log(other, self)

    def export(self, src: Source) -> gt.Sourced[T]:
        if hasattr(self.v, "export"):
            return gt.Sourced(self.v.export(src), self.s)
        return gt.Sourced(self.v, self.s)


class SourceMeta(type):
    name: str = ""
    priority: float | int

    def __lt__(cls, other):
        return cls.priority < other.priority

    def __str__(cls):
        return cls.name

    def __repr__(cls):
        return f"<{cls.__name__}>"

    def encode(cls, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return cls.name.encode(encoding, errors)


class Source(metaclass=SourceMeta):
    name: ClassVar[str]
    priority: ClassVar[float | int]
    g: rx.PyGraph

    def __init__(self, config: Config):
        self.g = rx.PyGraph()
        rich.print(INFO1 + f"Retrieving from {self.name}")

        if self.retrieve_from_cache(config) is not None:
            return
        self.build(config)
        self.save_to_cache(config)

    def build(self, config: Config):
        raise NotImplementedError

    def find_by_ref[R: NodeRef, N: Node](self, v: R) -> N | None:
        indices = self.g.filter_nodes(lambda a: v.refs(self, a))
        if len(indices) == 0:
            return None
        return self.g[indices[0]]

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    def find_by_ref_or_index[R: NodeRef, N: Node](self, v: R | int) -> N | None:
        from gatelogue_aggregator.types.node.base import NodeRef

        if isinstance(v, NodeRef):
            return self.find_by_ref(v)
        if isinstance(v, int):
            return self.g[v]
        raise TypeError(type(v))

    @classmethod
    def source[T](cls, v: T) -> Sourced[T]:
        return Sourced(v, s={cls.name})

    def retrieve_from_cache(self, config: Config) -> rx.PyGraph | None:
        if type(self).__name__ in config.cache_exclude:
            return None
        cache_file = config.cache_dir / "network-cache" / type(self).__name__
        if not cache_file.exists():
            return None
        rich.print(INFO1 + f"Retrieving from cache {cache_file}")
        self.g = pickle.loads(cache_file.read_bytes(), encoding="utf-8")  # noqa: S301
        if self.g.num_nodes() == 0:
            rich.print(ERROR + f"{type(self).__name__} yielded no results")
        return self.g

    def save_to_cache(self, config: Config):
        if self.g.num_nodes() == 0:
            rich.print(ERROR + f"{self.__name__} yielded no results")
        self.sanitise_strings()

        cache_file = config.cache_dir / "network-cache" / type(self).__name__
        rich.print(INFO1 + f"Saving to cache {cache_file}")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.touch()
        cache_file.write_bytes(pickle.dumps(self.g))

    def sanitise_strings(self):
        for node in self.g.nodes():
            node.sanitise_strings()
        for edge in self.g.edges():
            if hasattr(edge.v, "sanitise_strings"):
                edge.v.sanitise_strings()


