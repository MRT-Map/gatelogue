from __future__ import annotations

import dataclasses
import re
import uuid
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Self, TypeVar, override

import msgspec
import networkx as nx
import rich

if TYPE_CHECKING:
    from collections.abc import Callable, Generator


class ToSerializable:
    class Ser(msgspec.Struct, kw_only=True):
        pass


class BaseContext(ToSerializable):
    g: nx.MultiGraph[uuid.UUID]

    def __init__(self):
        self.g = nx.MultiGraph()


class Mergeable[CTX: BaseContext]:
    def equivalent(self, ctx: CTX, other: Self) -> bool:
        raise NotImplementedError

    def merge(self, ctx: CTX, other: Self):
        raise NotImplementedError

    def merge_if_equivalent(self, ctx: CTX, other: Self) -> bool:
        if self.equivalent(ctx, other):
            self.merge(ctx, other)
            return True
        return False

    @staticmethod
    def merge_lists[T: Mergeable](ctx: CTX, self: list[T], other: list[T]):
        for o in other:
            for s in self:
                if s.merge_if_equivalent(ctx, o):
                    break
            else:
                self.append(o)


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Node[CTX: BaseContext](Mergeable[CTX], ToSerializable):
    acceptable_list_node_types: Callable[[], ClassVar[tuple[type[Node], ...]]] = lambda: ()
    acceptable_single_node_types: Callable[[], ClassVar[tuple[type[Node], ...]]] = lambda: ()
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)

    def __init__(self, ctx: CTX, source: Source | None = None, **attrs):
        source = source or type(ctx)
        ctx.g.add_node(self, **{source: self.Attrs(**attrs)})

    # def ctx(self, ctx: BaseContext):
    #     raise NotImplementedError
    #
    # def de_ctx(self, ctx: BaseContext):
    #     raise NotImplementedError
    #
    # def update(self, ctx: BaseContext):
    #     raise NotImplementedError

    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs:
        pass

    def attrs(self, ctx: CTX, source: Source | None = None) -> Node.Attrs | None:
        source = source or type(ctx)
        return ctx.g[self.id].get(source)

    def all_attrs(self, ctx: CTX) -> dict[Source, Node.Attrs]:
        return ctx.g[self.id]

    def merged_attrs(self, ctx: CTX) -> dict[str, Any]:
        attrs = sorted(self.all_attrs(ctx).items())
        attr = {
            k: (Sourced(v, {attrs[0][0].name}) if v is not None else None)
            for k, v in dataclasses.asdict(attrs[0][1]).items()
        }
        for source, new_attr in attrs[1:]:
            new_attr = dataclasses.asdict(new_attr)
            for k, v in new_attr.items():
                if attr.get(k) is None and v is not None:
                    attr[k] = Sourced(v, {source.name})
                elif attr[k].v == v:
                    attr[k].s.add(source.name)
                elif isinstance(attr[k].v, set | dict):
                    attr[k].v.update(v)
                elif isinstance(attr[k].v, list):
                    attr[k].v.extend(v)
        return attr

    def connect(self, ctx: CTX, node: Node, source: Source | None = None):
        source = source or type(ctx)
        if type(node) not in self.acceptable_list_node_types():
            raise TypeError
        ctx.g.add_edge(self, node, source)

    def connect_one(self, ctx: CTX, node: Node, source: Source | None = None):
        source = source or type(ctx)
        if type(node) not in self.acceptable_single_node_types():
            raise TypeError
        if (prev := self.get_one(ctx, type(node))) is not None:
            self.disconnect_all(ctx, prev)
        ctx.g.add_edge(self, node, source)

    def disconnect_one(self, ctx: CTX, node: Node, source: Source | None = None):
        source = source or type(ctx)
        if type(node) not in self.acceptable_list_node_types() + self.acceptable_single_node_types():
            raise TypeError
        ctx.g.remove_edge(self, node, source)

    def disconnect_all(self, ctx: CTX, node: Node):
        if type(node) not in self.acceptable_list_node_types() + self.acceptable_single_node_types():
            raise TypeError
        for key in ctx.g[self][node]:
            ctx.g.remove_edge(self, node, key)

    def get_all[T: Node](self, ctx: CTX, ty: type[T]) -> Generator[T, None, None]:
        if ty not in self.acceptable_list_node_types():
            raise TypeError
        return (a for a in ctx.g.neighbors(self) if isinstance(a, ty))

    def get_all_ser[T: Node](self, ctx: CTX, ty: type[T]) -> list[Sourced.Ser[uuid.UUID]]:
        if ty not in self.acceptable_list_node_types():
            raise TypeError
        return [Sourced(a.id, {s.name for s in ctx.g[self][a]}).ser() for a in self.get_all(ctx, ty)]

    def get_one[T: Node](self, ctx: CTX, ty: type[T]) -> T | None:
        if ty not in self.acceptable_single_node_types():
            raise TypeError
        return next((a for a in ctx.g.neighbors(self) if isinstance(a, ty)), None)

    def get_one_ser[T: Node](self, ctx: CTX, ty: type[T]) -> Sourced.Ser[uuid.UUID] | None:
        if ty not in self.acceptable_single_node_types():
            raise TypeError
        node = self.get_one(ctx, ty)
        if node is None:
            return None
        return Sourced(node.id, {s.name for s in ctx.g[self][node]}).ser()

    def source(self, source: Sourced | Source) -> Sourced[Self]:
        return Sourced(self).source(source)

    @override
    def merge(self, ctx: CTX, other: Self):
        ctx.g[self.id].update(ctx.g[other.id])
        nx.contracted_nodes(ctx.g, self, other)


_T = TypeVar("_T")


class Sourced[T](msgspec.Struct, Mergeable, ToSerializable):
    v: T
    s: set[str] = msgspec.field(default_factory=set)

    @override
    class Ser(msgspec.Struct, Generic[_T]):
        v: _T
        s: set[str]

    def ser(self) -> Ser:
        return self.Ser(
            v=str(self.v.id) if isinstance(self.v, Node) else self.v.ser() if hasattr(self.v, "ser") else self.v,
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
        return self.v.equivalent(other.v) if isinstance(self.v, Mergeable) else self.v == other.v

    def merge(self, ctx: BaseContext, other: Self):
        if isinstance(self.v, Mergeable):
            self.v.merge(ctx, other.v)
        self.s.update(other.s)


class Source:
    name: ClassVar[str]

    def __init__(self):
        rich.print(f"[yellow]Retrieving from {self.name}")


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
