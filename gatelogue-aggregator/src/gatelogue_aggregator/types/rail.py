from __future__ import annotations

import dataclasses
import uuid
from typing import override, Container, Literal, Any, Self

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Source, Node, ToSerializable, Sourced


class _RailContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailCompany(Node[_RailContext]):
    acceptable_list_node_types = lambda: (RailLine, Station)

    @override
    def __init__(self, ctx: RailContext, source: type[RailContext] | None = None, *, name: str, **attrs):
        super().__init__(ctx, source, name=name, **attrs)

    @override
    def str_ctx(self, ctx: RailContext, filter_: Container[str] | None = None) -> str:
        name = self.merged_attr(ctx, "name")
        return name

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        name: str

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "name":
                return v
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            existing["name"].update(self.name)

    @override
    def attrs(self, ctx: RailContext, source: type[RailContext] | None = None) -> RailCompany.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: RailContext) -> dict[Source, RailCompany.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        name: str
        lines: list[Sourced.Ser[str]]
        stations: list[Sourced.Ser[str]]

    def ser(self, ctx: RailContext) -> RailCompany.Ser:
        return self.Ser(
            **self.merged_attrs(ctx), lines=self.get_all_ser(ctx, RailLine), stations=self.get_all_ser(ctx, Station)
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.merged_attr(ctx, "name") == other.merged_attr(ctx, "name")

    @override
    def key(self, ctx: RailContext) -> str:
        return self.merged_attr(ctx, "name")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailLine(Node[_RailContext]):
    acceptable_single_node_types = lambda: (RailCompany,)

    @override
    def __init__(self, ctx: RailContext, source: type[RailContext] | None = None, *, code: str, **attrs):
        super().__init__(ctx, source, code=code, **attrs)

    @override
    def str_ctx(self, ctx: RailContext, filter_: Container[str] | None = None) -> str:
        code = self.merged_attr(ctx, "code")
        return code

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str
        name: str | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            if k == "name":
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "name")

    @override
    def attrs(self, ctx: RailContext, source: type[RailContext] | None = None) -> RailLine.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: RailContext) -> dict[Source, RailLine.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        code: str
        company: Sourced.Ser[str]
        name: Sourced.Ser[str] | None = None

    def ser(self, ctx: RailContext) -> RailLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, RailCompany),
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.merged_attr(ctx, "code") == other.merged_attr(ctx, "code")

    @override
    def key(self, ctx: RailContext) -> str:
        return self.merged_attr(ctx, "code")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Station(Node[_RailContext]):
    acceptable_list_node_types = lambda: (Station,)
    acceptable_single_node_types = lambda: (RailCompany,)

    @override
    def __init__(self, ctx: RailContext, source: type[RailContext] | None = None, *, code: str, **attrs):
        super().__init__(ctx, source, code=code, **attrs)

    @override
    def str_ctx(self, ctx: RailContext, filter_: Container[str] | None = None) -> str:
        code = self.merged_attr(ctx, "name").v or self.merged_attr(ctx, "code")
        return code

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str
        name: str | None = None
        coordinates: tuple[int, int] | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            if k in ("name", "coordinates"):
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "name")
            self.sourced_merge(source, existing, "coordinates")

    @override
    def attrs(self, ctx: RailContext, source: type[RailContext] | None = None) -> Station.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: RailContext) -> dict[Source, Station.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        code: str
        company: Sourced.Ser[str]
        connections: dict[str, list[Sourced.Ser[Connection]]]
        name: Sourced.Ser[str] | None = None
        coordinates: Sourced.Ser[tuple[int, int]] | None = None

    def ser(self, ctx: RailContext) -> RailLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, RailCompany),
            connections={str(n.id): self.get_edges_ser(ctx, n, Connection) for n in self.get_all(ctx, Station)},
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.merged_attr(ctx, "code") == other.merged_attr(ctx, "code")

    @override
    def key(self, ctx: RailContext) -> str:
        return self.merged_attr(ctx, "code")


class Connection(msgspec.Struct, ToSerializable, kw_only=True, frozen=True):
    line: uuid.UUID
    direction: str | None = None


class RailContext(_RailContext):
    @override
    class Ser(msgspec.Struct):
        rail_company: dict[str, RailCompany.Ser]
        rail_line: dict[str, RailLine.Ser]
        station: dict[str, Station.Ser]

    def ser(self) -> RailContext.Ser:
        return RailContext.Ser(
            rail_company={str(a.id): a.ser(self) for a in self.g.nodes if isinstance(a, RailCompany)},
            rail_line={str(a.id): a.ser(self) for a in self.g.nodes if isinstance(a, RailLine)},
            station={str(a.id): a.ser(self) for a in self.g.nodes if isinstance(a, Station)},
        )

    def company(self, source: type[RailContext] | None = None, *, name: str, **attrs) -> RailCompany:
        for n in self.g.nodes:
            if not isinstance(n, RailCompany):
                continue
            if n.merged_attr(self, "name") == name:
                return n
        return RailCompany(self, source, name=name, **attrs)

    def line(self, source: type[RailContext] | None = None, *, code: str, **attrs) -> RailLine:
        for n in self.g.nodes:
            if not isinstance(n, RailLine):
                continue
            if n.merged_attr(self, "code") == code:
                return n
        return RailLine(self, source, code=code, **attrs)

    def station(self, source: type[RailContext] | None = None, *, code: str, **attrs) -> Station:
        for n in self.g.nodes:
            if not isinstance(n, Station):
                continue
            if n.merged_attr(self, "code") == code:
                return n
        return Station(self, source, code=code, **attrs)


class RailSource(RailContext, Source):
    pass
