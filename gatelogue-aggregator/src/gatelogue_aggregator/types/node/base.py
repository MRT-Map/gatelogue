from __future__ import annotations

import copy
import dataclasses
import re
import uuid
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self, override

import networkx as nx

from gatelogue_aggregator.types.base import BaseContext, Mergeable, Source, Sourced, ToSerializable
from gatelogue_aggregator.types.connections import Proximity
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from collections.abc import Callable, Container, Hashable, Iterator


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Node[CTX: BaseContext](Mergeable[CTX], ToSerializable):
    acceptable_list_node_types: Callable[[], ClassVar[tuple[type[Node], ...]]] = lambda: ()
    acceptable_single_node_types: Callable[[], ClassVar[tuple[type[Node], ...]]] = lambda: ()
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)

    def __init__(self, ctx: CTX, source: Source | None = None, **attrs):
        self.id = uuid.uuid4()
        source = source or type(ctx)
        ctx.g.add_node(self)
        ctx.g.nodes[self][source] = self.Attrs(**attrs)

    def str_ctx(self, ctx: CTX) -> str:
        return (
            type(self).__name__
            + "("
            + ",".join(f"{k}={v}" for k, v in self.merged_attrs(ctx).items() if v is not None)
            + ")"
        )

    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError

        @staticmethod
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            raise NotImplementedError

        def merge_into(self, source: Source, existing: dict[str, Any]):
            raise NotImplementedError

        def sourced_merge(self, source: Source, existing: dict[str, Any], attr: str):
            if attr not in existing:
                return
            if existing[attr] is not None and getattr(self, attr) == existing[attr].v:
                existing[attr].s.add(source.name)
            if getattr(self, attr) is not None:
                existing[attr] = existing[attr] or Sourced(getattr(self, attr)).source(source)

    def attrs(self, ctx: CTX, source: Source | None = None) -> Node.Attrs | None:
        source = source or type(ctx)
        return ctx.g.nodes[self].get(source)

    def all_attrs(self, ctx: CTX) -> dict[Source, Node.Attrs]:
        return ctx.g.nodes[self]

    def merged_attrs(self, ctx: CTX, filter_: Container[str] | None = None) -> dict[str, Any]:
        attrs = sorted(self.all_attrs(ctx).items())
        attr = {
            k: type(attrs[0][1]).prepare_merge(attrs[0][0], k, v) if v is not None else None
            for k, v in dataclasses.asdict(attrs[0][1]).items()
            if (True if filter_ is None else k in filter_)
        }
        for source, new_attr in attrs[1:]:
            new_attr.merge_into(source, attr)
        return attr

    def merged_attr[T](self, ctx: CTX, attr: str, _: type[T] = Any) -> T:
        return self.merged_attrs(ctx, (attr,))[attr]

    def connect(
        self, ctx: CTX, node: Node, value: Any | None = None, source: Source | None = None, key: Hashable | None = None
    ):
        source = source or type(ctx)
        if not any(isinstance(node, a) for a in type(self).acceptable_list_node_types()):
            raise TypeError
        ctx.g.add_edge(self, node, key, v=value, s=source)

    def connect_one(
        self, ctx: CTX, node: Node, value: Any | None = None, source: Source | None = None, key: Any | None = None
    ):
        source = source or type(ctx)
        key = key or source
        if not any(isinstance(node, a) for a in type(self).acceptable_single_node_types()):
            raise TypeError
        if (prev := self.get_one(ctx, type(node))) is not None:
            self.disconnect(ctx, prev)
        ctx.g.add_edge(self, node, key, v=value, s=source)

    def disconnect(self, ctx: CTX, node: Node):
        if not any(
            isinstance(node, a)
            for a in type(self).acceptable_list_node_types() + type(self).acceptable_single_node_types()
        ):
            raise TypeError
        d = copy.deepcopy(ctx.g[self][node])
        for key in d:
            ctx.g.remove_edge(self, node, key)

    @staticmethod
    def _get_sources(d: dict[Literal["contraction"] | type[Source] | int, Any]) -> Iterator[str]:
        for k, v in d.items():
            if k == "contraction":
                yield from Node._get_sources(v)
            elif hasattr(v["s"], "name"):
                yield v["s"].name

    def get_all[T: Node](self, ctx: CTX, ty: type[T], conn_ty: type | None = None) -> Iterator[T]:
        if ty not in type(self).acceptable_list_node_types():
            raise TypeError
        return (
            a
            for a in ctx.g.neighbors(self)
            if isinstance(a, ty)
            and (True if conn_ty is None else any(isinstance(b["v"], conn_ty) for b in ctx.g[self][a].values()))
        )

    def get_all_ser[T: Node](self, ctx: CTX, ty: type[T], conn_ty: type | None = None) -> list[Sourced.Ser[uuid.UUID]]:
        if ty not in type(self).acceptable_list_node_types():
            raise TypeError
        return [Sourced(a.id, set(Node._get_sources(ctx.g[self][a]))).ser(ctx) for a in self.get_all(ctx, ty, conn_ty)]

    def get_one[T: Node](self, ctx: CTX, ty: type[T], conn_ty: type | None = None) -> T | None:
        if ty not in type(self).acceptable_single_node_types():
            raise TypeError
        return next(
            (
                a
                for a in ctx.g.neighbors(self)
                if isinstance(a, ty)
                and (True if conn_ty is None else any(isinstance(b["v"], conn_ty) for b in ctx.g[self][a].values()))
            ),
            None,
        )

    def get_one_ser[T: Node](self, ctx: CTX, ty: type[T], conn_ty: type | None = None) -> Sourced.Ser[uuid.UUID] | None:
        if ty not in type(self).acceptable_single_node_types():
            raise TypeError
        node = self.get_one(ctx, ty, conn_ty)
        if node is None:
            return None
        return Sourced(node.id, set(Node._get_sources(ctx.g[self][node]))).ser(ctx)

    def get_edges[T: Node](self, ctx: CTX, node: Node, ty: type[T] | None = None) -> Iterator[T]:
        return (a["v"] for a in ctx.g[self][node].values() if (True if ty is None else isinstance(a["v"], ty)))

    def get_edges_ser[T](self, ctx: CTX, node: Node, ty: type[T] | None = None) -> list[Sourced.Ser[T]]:
        return [
            Sourced(v["v"], {v["s"].name} if hasattr(v["s"], "name") else {}).ser(ctx)
            for v in ctx.g[self][node].values()
            if (True if ty is None else isinstance(v["v"], ty))
        ]

    def source(self, source: Sourced | Source) -> Sourced[Self]:
        return Sourced(self).source(source)

    @override
    def merge(self, ctx: CTX, other: Self):
        attrs = ctx.g.nodes[self]
        attrs.update(ctx.g.nodes[other])
        nx.contracted_nodes(ctx.g, self, other, copy=False)
        del attrs["contraction"]

    def merge_key(self, ctx: CTX) -> str:
        raise NotImplementedError

    @staticmethod
    def process_code[T: (str, None)](s: T) -> T:
        if s is None:
            return None
        res = ""
        hyphen1 = False
        hyphen2 = False
        for match in search_all(re.compile(r"\d+|[A-Za-z]+|[^\dA-Za-z]+"), str(s).strip()):
            t = match.group(0)
            if len(t) == 0:
                continue
            if (
                (hyphen1 and t[0].isdigit())
                or (hyphen2 and t[0].isalpha())
                or (len(res) != 0 and t[0].isdigit() and res[-1].isdigit())
            ):
                res += "-"
            if hyphen1:
                hyphen1 = False
            if hyphen2:
                hyphen2 = False
            if t.isdigit():
                res += t.lstrip("0") or "0"
            elif t.isalpha():
                res += t.upper()
            elif (t == "-" and len(res) == 0) or (len(res) != 0 and res[-1].isdigit()):
                hyphen1 = True
            elif len(res) != 0 and res[-1].isalpha():
                hyphen2 = True

        return res


class LocatedNode[CTX](Node[CTX]):
    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        world: Literal["New", "Old"] | None = None
        coordinates: tuple[int, int] | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k in ("coordinates", "world"):
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "world")
            self.sourced_merge(source, existing, "coordinates")

    @override
    class Ser(Node.Ser, kw_only=True):
        import uuid
        from typing import Literal

        coordinates: Sourced.Ser[tuple[int, int]] | None
        """Coordinates of the object"""
        world: Sourced.Ser[Literal["New", "Old"]] | None
        """Whether the object is in the New or Old world"""
        proximity: dict[str, dict[uuid.UUID, Sourced.Ser[Proximity]]]
        """
        References all objects that are near (within walking distance of) this object.
        It is represented as a mapping of object types to a inner mapping of object IDs to proximity data (:py:class:`Proximity`).
        For example, ``{"airport": {1234: <proximity>}}`` means that there is an airport with ID ``1234`` near this object, and ``<proximity>`` is a :py:class:`Proximity` object.
        """

    def get_proximity_ser(self, ctx: CTX) -> dict[str, dict[uuid.UUID, Sourced.Ser[Proximity]]]:
        out = {}
        for node in self.get_all(ctx, LocatedNode):
            for edge in self.get_edges_ser(ctx, node, Proximity):
                out.setdefault(type(node).__name__.lower(), {})[node.id] = edge
        return out
