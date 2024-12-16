from __future__ import annotations

import re
from collections.abc import Callable  # noqa: TCH003
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self, override

import msgspec
import rustworkx as rx

from gatelogue_aggregator.types.base import Mergeable
from gatelogue_aggregator.types.context.shared_facility import SharedFacility
from gatelogue_aggregator.types.source import Source, Sourced
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from collections.abc import Iterator

    from gatelogue_aggregator.types.base import BaseContext
    from gatelogue_aggregator.types.context.proximity import Proximity


class Node[CTX: BaseContext | Source](Mergeable[CTX], msgspec.Struct, kw_only=True):
    acceptable_list_node_types: ClassVar[Callable[[], tuple[type[Node], ...]]] = lambda: ()
    acceptable_single_node_types: ClassVar[Callable[[], tuple[type[Node], ...]]] = lambda: ()
    i: int = None
    source: set[type[Source]] = msgspec.field(default_factory=set)

    @classmethod
    def new(cls, ctx: CTX, **kwargs) -> Self:
        self = cls(**kwargs)
        self.i = ctx.g.add_node(self)
        self.source.add(type(ctx))
        return self

    def str_ctx(self, _ctx: CTX) -> str:
        return (
            type(self).__name__
            + "("
            + ",".join(f"{k}={v}" for k, v in msgspec.structs.asdict(self).items() if v is not None)
            + ")"
        )

    def connect(
        self,
        ctx: CTX,
        node: Node,
        value: Any | None = None,
        source: set[type[Source]] | None = None,
    ):
        source = source or {type(ctx)}
        if not any(isinstance(node, a) for a in type(self).acceptable_list_node_types()):
            raise TypeError
        ctx.g.add_edge(self.i, node.i, Sourced(value, source))

    def connect_one(
        self,
        ctx: CTX,
        node: Node,
        value: Any | None = None,
        source: set[type[Source]] | None = None,
    ):
        source = source or {type(ctx)}
        if not any(isinstance(node, a) for a in type(self).acceptable_single_node_types()):
            raise TypeError
        if (prev := self.get_one(ctx, type(node))) is not None:
            self.disconnect(ctx, prev)
        ctx.g.add_edge(self.i, node.i, Sourced(value, source))

    def disconnect(self, ctx: CTX, node: Node):
        if not any(
            isinstance(node, a)
            for a in type(self).acceptable_list_node_types() + type(self).acceptable_single_node_types()
        ):
            raise TypeError
        while True:
            try:
                ctx.g.remove_edge(self.i, node.i)
            except rx.NoEdgeBetweenNodes:
                return

    def get_all[T: Node](self, ctx: CTX, ty: type[T], conn_ty: type | None = None) -> Iterator[T]:
        if ty not in type(self).acceptable_list_node_types():
            raise TypeError
        return (
            ctx.g[a]
            for a in ctx.g.neighbors(self.i)
            if isinstance(ctx.g[a], ty)
            and (
                True
                if conn_ty is None
                else any(
                    isinstance(b.v, conn_ty) if isinstance(b, Sourced) else False
                    for b in ctx.g.get_all_edge_data(self.i, a)
                )
            )
        )

    def get_all_id(self, ctx: CTX, ty: type[Node], conn_ty: type | None = None) -> list[Sourced[int]]:
        return [Sourced(a.i).source(next(self.get_edges(ctx, a, conn_ty))) for a in self.get_all(ctx, ty, conn_ty)]

    def get_one[T: Node](self, ctx: CTX, ty: type[T], conn_ty: type | None = None) -> T | None:
        if ty not in type(self).acceptable_single_node_types() and ty not in type(self).acceptable_list_node_types():
            raise TypeError
        return next(
            (
                ctx.g[a]
                for a in ctx.g.neighbors(self.i)
                if isinstance(ctx.g[a], ty)
                and (
                    True
                    if conn_ty is None
                    else any(
                        isinstance(b.v, conn_ty) if isinstance(b, Sourced) else False
                        for b in ctx.g.get_all_edge_data(self.i, a)
                    )
                )
            ),
            None,
        )

    def get_one_id(self, ctx: CTX, ty: type[Node], conn_ty: type | None = None) -> Sourced[int] | None:
        if (n := self.get_one(ctx, ty, conn_ty)) is None:
            return None
        return Sourced(n.i).source(next(self.get_edges(ctx, n, conn_ty)))

    def get_edges[T](self, ctx: CTX, node: Node, ty: type[T] | None = None) -> Iterator[Sourced[T]]:
        def filter_(edge: Sourced[Any]):
            if ty is None:
                return True
            return isinstance(edge.v, ty) if isinstance(edge, Sourced) else False

        try:
            return (a for a in ctx.g.get_all_edge_data(self.i, node.i) if filter_(a))
        except rx.NoEdgeBetweenNodes:
            return (a for a in [])

    def get_edge[T](self, ctx: CTX, node: Node, ty: type[T] | None = None) -> Sourced[T] | None:
        return next(self.get_edges(ctx, node, ty), None)

    @override
    def merge(self, ctx: CTX, other: Self):
        self.merge_attrs(ctx, other)
        self.source.update(other.source)
        self.i = ctx.g.contract_nodes((self.i, other.i), self)

    def _merge_sourced(self, ctx: CTX, other: Self, attr: str):
        self_attr: Sourced | None = getattr(self, attr)
        other_attr: Sourced | None = getattr(other, attr)
        match (self_attr, other_attr):
            case (None, None):
                pass
            case (_, None):
                pass
            case (None, _):
                setattr(self, attr, other_attr)
            case (_, _):
                self_attr.merge(ctx, other_attr)

    def merge_attrs(self, ctx: CTX, other: Self):
        raise NotImplementedError

    def merge_key(self, ctx: CTX) -> str:
        raise NotImplementedError

    def sanitise_strings(self):
        raise NotImplementedError

    def prepare_export(self, ctx: CTX):
        raise NotImplementedError

    def ref(self, ctx: CTX) -> NodeRef[Self]:
        raise NotImplementedError

    @staticmethod
    def process_code[T: (str, None)](s: T) -> T:
        if s is None or str(s).strip().lower() in ("", "?", "-", "foobar"):
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


class LocatedNode[CTX: BaseContext | Source](Node[CTX], kw_only=True):
    from gatelogue_aggregator.types.context.proximity import Proximity

    coordinates: Sourced[tuple[int, int]] | None = None
    """Coordinates of the object"""
    world: Sourced[World] | None = None
    """Whether the object is in the New or Old world"""

    proximity: dict[int, Sourced[Proximity]] = None
    """
    References all objects that are near (within walking distance of) this object.
    It is represented as an inner mapping of object IDs to proximity data (:py:class:`Proximity`).
    For example, ``{1234: <proximity>}`` means that there is an object with ID ``1234`` near this object, and ``<proximity>`` is a :py:class:`Proximity` object.
    """
    shared_facility: list[Sourced[int]] = None
    """References all objects that this object shares the same facility with (same building, station, hub etc)"""

    @classmethod
    def new(
        cls,
        ctx: CTX,
        *,
        world: World | None = None,
        coordinates: tuple[int, int] | None = None,
        **kwargs,
    ) -> Self:
        self = super().new(ctx, **kwargs)
        if world is not None:
            self.world = ctx.source(world)
        if coordinates is not None:
            self.coordinates = ctx.source(coordinates)
        return self

    @override
    def merge_attrs(self, ctx: CTX, other: Self):
        self._merge_sourced(ctx, other, "coordinates")
        self._merge_sourced(ctx, other, "world")

    @override
    def sanitise_strings(self):
        if self.world is not None:
            self.world.v = str(self.world.v).strip()

    @override
    def prepare_export(self, ctx: CTX):
        from gatelogue_aggregator.types.context.proximity import Proximity

        self.proximity = {
            node.i: b for node in self.get_all(ctx, LocatedNode) for b in self.get_edges(ctx, node, Proximity)
        }
        self.shared_facility = self.get_all_id(ctx, LocatedNode, SharedFacility)


class NodeRef[T: Node]:
    t: type[T]
    d: dict[str, Any]

    def __init__(self, t: type[T], **kwargs):
        self.t = t
        self.d = kwargs

    def __repr__(self):
        return f"Ref@{self.t.__name__}" + "(" + ",".join(f"{k}={v}" for k, v in self.d.items() if v is not None) + ")"

    def refs(self, ctx: BaseContext, node: Node) -> bool:
        if not isinstance(node, self.t):
            return False
        node_ref = node.ref(ctx)
        has_match = False
        for k, v in self.d.items():
            if k not in node_ref.d and v is not None:
                continue
            if isinstance(v, set):
                if len(v.intersection(node_ref.d[k])) == 0:
                    return False
            elif isinstance(v, Mergeable):
                if not v.equivalent(ctx, node_ref.d[k]):
                    return False
            elif v != node_ref.d[k]:
                return False
            has_match = True
        return has_match


World = Literal["New", "Old", "Space"]
