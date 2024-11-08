from __future__ import annotations

import dataclasses
import re
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self, cast, get_args, override

import msgspec
import rustworkx as rx

from gatelogue_aggregator.types.base import BaseContext, Mergeable, Source, Sourced
from gatelogue_aggregator.types.connections import Proximity
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Node[CTX: BaseContext](Mergeable[CTX], msgspec.Struct):
    acceptable_list_node_types: ClassVar[Callable[[], tuple[type[Node], ...]]] = lambda: ()
    acceptable_single_node_types: ClassVar[Callable[[], tuple[type[Node], ...]]] = lambda: ()
    i: int = None

    def __init__(self, ctx: CTX):
        super().__init__()
        self.i = ctx.g.add_node(self)

    def str_ctx(self, _ctx: CTX) -> str:
        return (
            type(self).__name__
            + "("
            + ",".join(f"{k}={v}" for k, v in msgspec.structs.asdict(self) if v is not None)
            + ")"
        )

    def connect(
        self,
        ctx: CTX,
        node: Node,
        value: Any | None = None,
    ):
        if not any(isinstance(node, a) for a in type(self).acceptable_list_node_types()):
            raise TypeError
        ctx.g.add_edge(self.i, node.i, value)

    def connect_one(
        self,
        ctx: CTX,
        node: Node,
        value: Any | None = None,
    ):
        if not any(isinstance(node, a) for a in type(self).acceptable_single_node_types()):
            raise TypeError
        if (prev := self.get_one(ctx, type(node))) is not None:
            self.disconnect(ctx, prev)
        ctx.g.add_edge(self.i, node.i, value)

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
            a
            for a in ctx.g.neighbors(self.i)
            if isinstance(a, ty)
            and (True if conn_ty is None else any(isinstance(b, conn_ty) for b in ctx.g.get_all_edge_data(self, a)))
        )

    def get_all_id(self, ctx: CTX, ty: type[Node], conn_ty: type | None = None) -> list[Sourced[int]]:
        return [Sourced(a.i).source(next(self.get_edges(ctx, a, conn_ty))) for a in self.get_all(ctx, ty, conn_ty)]

    def get_one[T: Node](self, ctx: CTX, ty: type[T], conn_ty: type | None = None) -> T | None:
        return next(self.get_all(ctx, ty, conn_ty), None)

    def get_one_id(self, ctx: CTX, ty: type[Node], conn_ty: type | None = None) -> Sourced[int] | None:
        if (n := self.get_one(ctx, ty, conn_ty)) is None:
            return None
        return Sourced(n.i).source(next(self.get_edges(ctx, n, conn_ty)))

    def get_edges[T](self, ctx: CTX, node: Node, ty: type[T] | None = None) -> Iterator[T]:
        def filter_(edge):
            if ty is None:
                return True
            if not isinstance(ty, Sourced):
                return isinstance(edge, cast(type[T], ty))
            if not isinstance(edge, Sourced):
                return False
            return isinstance(edge.v, get_args(ty)[0])

        return (a for a in ctx.g.get_all_edge_data(self, node) if filter_(a))

    @override
    def merge(self, ctx: CTX, other: Self):
        self.merge_attrs(ctx, other)
        self.i = ctx.g.contract_nodes((self.i, other.i), self)

    def _merge_sourced(self, ctx: CTX, other: Self, attr: str):
        self_attr: Sourced | None = getattr(self, attr)
        other_attr: Sourced | None = getattr(self, other)
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

    def prepare_export(self, ctx: CTX):
        raise NotImplementedError

    def ref(self, ctx: CTX) -> NodeRef[Self]:
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


class LocatedNode[CTX: BaseContext | Source](Node[CTX]):
    coordinates: Sourced[tuple[int, int]] | None = None
    """Coordinates of the object"""
    world: Sourced[Literal["New", "Old"]] | None = None
    """Whether the object is in the New or Old world"""

    proximity: dict[int, Sourced[Proximity]] = None
    """
    References all objects that are near (within walking distance of) this object.
    It is represented as an inner mapping of object IDs to proximity data (:py:class:`Proximity`).
    For example, ``{1234: <proximity>}`` means that there is an object with ID ``1234`` near this object, and ``<proximity>`` is a :py:class:`Proximity` object.
    """

    def __init__(
        self,
        ctx: CTX,
        *,
        world: Literal["New", "Old"] | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        super().__init__(ctx)
        if world is not None:
            self.world = ctx.source(world)
        if coordinates is not None:
            self.coordinates = ctx.source(coordinates)

    @override
    def merge_attrs(self, ctx: CTX, other: Self):
        self._merge_sourced(ctx, other, "coordinates")
        self._merge_sourced(ctx, other, "world")

    @override
    def prepare_export(self, ctx: CTX):
        self.proximity = {
            node.i: b for node in self.get_all(ctx, LocatedNode) for b in self.get_edges(ctx, node, Sourced[Proximity])
        }


class NodeRef[T: Node]:
    t: type[T]
    d: dict[str, Any]

    def __init__(self, t: type[T], **kwargs):
        self.t = t
        self.d = kwargs

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
