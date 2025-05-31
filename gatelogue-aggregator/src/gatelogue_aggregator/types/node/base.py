from __future__ import annotations

import re
from collections.abc import Callable  # noqa: TCH003
from typing import TYPE_CHECKING, Any, ClassVar, Self, override

import rich

import gatelogue_types as gt
import msgspec
import rustworkx as rx

from gatelogue_aggregator.logging import ERROR
from gatelogue_aggregator.types.edge.shared_facility import SharedFacility
from gatelogue_aggregator.types.mergeable import Mergeable
from gatelogue_aggregator.types.source import Source, Sourced
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from collections.abc import Iterator


class Node(gt.Node, Mergeable, msgspec.Struct, kw_only=True):
    acceptable_list_node_types: ClassVar[Callable[[], tuple[type[Node], ...]]] = lambda: ()
    acceptable_single_node_types: ClassVar[Callable[[], tuple[type[Node], ...]]] = lambda: ()

    @classmethod
    def new(cls, src: Source, **kwargs) -> Self:
        self = cls(**kwargs)
        self.i = src.g.add_node(self)
        self.source.add(type(src).__name__)
        return self

    def str_src(self, _src: Source) -> str:
        return str(self)

    def connect(
        self,
        src: Source,
        node: Node,
        value: Any | None = None,
        source: set[str] | None = None,
    ):
        source = source or {type(src)}
        if not any(isinstance(node, a) for a in type(self).acceptable_list_node_types()):
            raise TypeError
        src.g.add_edge(self.i, node.i, Sourced(value, source))

    def connect_one(
        self,
        src: Source,
        node: Node,
        value: Any | None = None,
        source: set[str] | None = None,
    ):
        source = source or {type(src)}
        if not any(isinstance(node, a) for a in type(self).acceptable_single_node_types()):
            raise TypeError
        if (prev := self.get_one(src, type(node))) is not None:
            self.disconnect(src, prev)
        src.g.add_edge(self.i, node.i, Sourced(value, source))

    def disconnect(self, src: Source, node: Node):
        if not any(
            isinstance(node, a)
            for a in type(self).acceptable_list_node_types() + type(self).acceptable_single_node_types()
        ):
            raise TypeError
        while True:
            try:
                src.g.remove_edge(self.i, node.i)
            except rx.NoEdgeBetweenNodes:
                return

    def get_all[T: Node](self, src: Source, ty: type[T], conn_ty: type | None = None) -> Iterator[T]:
        if ty not in type(self).acceptable_list_node_types():
            raise TypeError
        return (
            src.g[a]
            for a in src.g.neighbors(self.i)
            if isinstance(src.g[a], ty)
            and (
                True
                if conn_ty is None
                else any(
                    isinstance(b.v, conn_ty) if isinstance(b, Sourced) else False
                    for b in src.g.get_all_edge_data(self.i, a)
                )
            )
        )

    def get_all_id(self, src: Source, ty: type[Node], conn_ty: type | None = None) -> list[Sourced[int]]:
        return [Sourced(a.i).source(next(self.get_edges(src, a, conn_ty))) for a in self.get_all(src, ty, conn_ty)]

    def get_one[T: Node](self, src: Source, ty: type[T], conn_ty: type | None = None) -> T | None:
        if ty not in type(self).acceptable_single_node_types() and ty not in type(self).acceptable_list_node_types():
            raise TypeError
        return next(
            (
                src.g[a]
                for a in src.g.neighbors(self.i)
                if isinstance(src.g[a], ty)
                and (
                    True
                    if conn_ty is None
                    else any(
                        isinstance(b.v, conn_ty) if isinstance(b, Sourced) else False
                        for b in src.g.get_all_edge_data(self.i, a)
                    )
                )
            ),
            None,
        )

    def get_one_id(self, src: Source, ty: type[Node], conn_ty: type | None = None) -> Sourced[int] | None:
        if (n := self.get_one(src, ty, conn_ty)) is None:
            return None
        return Sourced(n.i).source(next(self.get_edges(src, n, conn_ty)))

    def get_edges[T](self, src: Source, node: Node, ty: type[T] | None = None) -> Iterator[Sourced[T]]:
        def filter_(edge: Sourced[Any]):
            if ty is None:
                return True
            return isinstance(edge.v, ty) if isinstance(edge, Sourced) else False

        try:
            return (a for a in src.g.get_all_edge_data(self.i, node.i) if filter_(a))
        except rx.NoEdgeBetweenNodes:
            return (a for a in [])

    def get_edge[T](self, src: Source, node: Node, ty: type[T] | None = None) -> Sourced[T] | None:
        return next(self.get_edges(src, node, ty), None)

    @override
    def merge(self, src: Source, other: Self):
        self.merge_attrs(src, other)
        self.source.update(other.source)
        self.i = src.g.contract_nodes((self.i, other.i), self)

    def _merge_sourced(self, src: Source, other: Self, attr: str):
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
                self_attr.merge(src, other_attr, log_src=(self, attr))

    def merge_attrs(self, src: Source, other: Self):
        raise NotImplementedError

    def merge_key(self, src: Source) -> str:
        raise NotImplementedError

    def sanitise_strings(self):
        raise NotImplementedError

    def export(self, src: Source) -> gt.Node:
        return gt.Node(**self._as_dict(src))

    def _as_dict(self, _src: Source) -> dict:
        return msgspec.structs.asdict(self)

    def ref(self, src: Source) -> NodeRef[Self]:
        raise NotImplementedError

    def report(self, src: Source):
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


class LocatedNode(gt.LocatedNode, Node, kw_only=True):
    @classmethod
    def new(
        cls,
        src: Source,
        *,
        world: gt.World | None = None,
        coordinates: tuple[float, float] | None = None,
        **kwargs,
    ) -> Self:
        self = super().new(src, **kwargs)
        if world is not None:
            self.world = src.source(world)
        if coordinates is not None:
            self.coordinates = src.source(coordinates)
        return self

    @override
    def merge_attrs(self, src: Source, other: Self):
        self._merge_sourced(src, other, "coordinates")
        self._merge_sourced(src, other, "world")

    @override
    def sanitise_strings(self):
        if self.world is not None:
            self.world.v = str(self.world.v).strip()

    @override
    def export(self, src: Source) -> gt.LocatedNode:
        return gt.LocatedNode(**self._as_dict(src))

    @override
    def _as_dict(self, src: Source) -> dict:
        return super()._as_dict(src) | {
            "proximity": {
                node.i: b.export(src)
                for node in self.get_all(src, LocatedNode)
                for b in self.get_edges(src, node, gt.Proximity)
            },
            "shared_facility": self.get_all_id(src, LocatedNode, SharedFacility),
        }

    @override
    def report(self, src: Source):
        if self.coordinates is None:
            rich.print(ERROR + type(self).__name__ + " " + self.str_src(src) + " has no coordinates")
        if self.world is None:
            rich.print(ERROR + type(self).__name__ + " " + self.str_src(src) + " has no world")


class NodeRef[T: Node]:
    t: type[T]
    d: dict[str, Any]

    def __init__(self, t: type[T], **kwargs):
        self.t = t
        self.d = kwargs

    def __repr__(self):
        return f"Ref@{self.t.__name__}" + "(" + ",".join(f"{k}={v}" for k, v in self.d.items() if v is not None) + ")"

    def refs(self, src: Source, node: Node) -> bool:
        if not isinstance(node, self.t):
            return False
        node_ref = node.ref(src)
        has_match = False
        for k, v in self.d.items():
            if k not in node_ref.d and v is not None:
                continue
            if isinstance(v, set):
                if len(v.intersection(node_ref.d[k])) == 0:
                    return False
            elif isinstance(v, Mergeable):
                if not v.equivalent(src, node_ref.d[k]):
                    return False
            elif v != node_ref.d[k]:
                return False
            has_match = True
        return has_match
