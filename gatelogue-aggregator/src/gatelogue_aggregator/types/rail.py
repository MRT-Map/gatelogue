from __future__ import annotations

import dataclasses
import typing
from typing import TYPE_CHECKING, Any, Literal, Self, override

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Node, Source, Sourced, ToSerializable

if TYPE_CHECKING:
    import uuid
    from collections.abc import Container, Callable


class _RailContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailCompany(Node[_RailContext]):
    acceptable_list_node_types = lambda: (RailLine, Station)  # noqa: E731

    @override
    def __init__(self, ctx: RailContext, source: type[RailContext] | None = None, *, name: str, **attrs):
        super().__init__(ctx, source, name=name, **attrs)

    @override
    def str_ctx(self, ctx: RailContext, filter_: Container[str] | None = None) -> str:
        return self.merged_attr(ctx, "name")

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
            pass

    @override
    def attrs(self, ctx: RailContext, source: type[RailContext] | None = None) -> RailCompany.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: RailContext) -> dict[Source, RailCompany.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        name: str
        lines: list[Sourced.Ser[uuid.UUID]]
        stations: list[Sourced.Ser[uuid.UUID]]

    def ser(self, ctx: RailContext) -> RailCompany.Ser:
        return self.Ser(
            **self.merged_attrs(ctx), lines=self.get_all_ser(ctx, RailLine), stations=self.get_all_ser(ctx, Station)
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.merged_attr(ctx, "name") == other.merged_attr(ctx, "name")

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.merged_attr(ctx, "name")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailLine(Node[_RailContext]):
    acceptable_single_node_types = lambda: (RailCompany,)  # noqa: E731

    @override
    def __init__(
        self, ctx: RailContext, source: type[RailContext] | None = None, *, code: str, company: RailCompany, **attrs
    ):
        super().__init__(ctx, source, code=code, **attrs)
        self.connect_one(ctx, company)

    @override
    def str_ctx(self, ctx: RailContext, filter_: Container[str] | None = None) -> str:
        code = self.merged_attr(ctx, "code")
        company = self.get_one(ctx, RailCompany).merged_attr(ctx, "name")
        return f"{company} {code}"

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str
        mode: Literal["warp", "cart", "traincart", "vehicles"] | None = None
        name: str | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            if k in ("name", "mode"):
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "name")
            self.sourced_merge(source, existing, "mode")

    @override
    def attrs(self, ctx: RailContext, source: type[RailContext] | None = None) -> RailLine.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: RailContext) -> dict[Source, RailLine.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        code: str
        company: Sourced.Ser[uuid.UUID]
        mode: Sourced.Ser[Literal["warp", "cart", "traincart", "vehicles"]] | None = None
        name: Sourced.Ser[str] | None = None

    def ser(self, ctx: RailContext) -> RailLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, RailCompany),
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.merged_attr(ctx, "code") == other.merged_attr(ctx, "code") and self.get_one(
            ctx, RailCompany
        ).equivalent(ctx, other.get_one(ctx, RailCompany))

    @override
    def merge(self, ctx: RailContext, other: Self):
        msg = "Cannot merge"
        raise TypeError(msg)

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.merged_attr(ctx, "code")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Station(Node[_RailContext]):
    acceptable_list_node_types = lambda: (Station,)  # noqa: E731
    acceptable_single_node_types = lambda: (RailCompany,)  # noqa: E731

    @override
    def __init__(
        self,
        ctx: RailContext,
        source: type[RailContext] | None = None,
        *,
        codes: set[str],
        company: RailCompany,
        **attrs,
    ):
        super().__init__(ctx, source, codes=codes, **attrs)
        self.connect_one(ctx, company)

    @override
    def str_ctx(self, ctx: RailContext, filter_: Container[str] | None = None) -> str:
        code = "/".join(self.merged_attr(ctx, "codes")) if (code := self.merged_attr(ctx, "name")) is None else code.v
        company = self.get_one(ctx, RailCompany).merged_attr(ctx, "name")
        return f"{company} {code}"

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        codes: set[str]
        name: str | None = None
        world: Literal["New", "Old"] | None = None
        coordinates: tuple[int, int] | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "codes":
                return v
            if k in ("name", "coordinates", "world"):
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            if "codes" in existing:
                existing["codes"].update(self.codes)
            self.sourced_merge(source, existing, "name")
            self.sourced_merge(source, existing, "world")
            self.sourced_merge(source, existing, "coordinates")

    @override
    def attrs(self, ctx: RailContext, source: type[RailContext] | None = None) -> Station.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: RailContext) -> dict[Source, Station.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        codes: str
        company: Sourced.Ser[uuid.UUID]
        connections: dict[str, list[Sourced.Ser[Connection]]]
        name: Sourced.Ser[str] | None = None
        world: Sourced.Ser[Literal["New", "Old"]] | None = None
        coordinates: Sourced.Ser[tuple[int, int]] | None = None

    def ser(self, ctx: RailContext) -> RailLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, RailCompany),
            connections={str(n.id): self.get_edges_ser(ctx, n, Connection) for n in self.get_all(ctx, Station)},
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return len(self.merged_attr(ctx, "codes").intersection(other.merged_attr(ctx, "codes"))) != 0 and self.get_one(
            ctx, RailCompany
        ).equivalent(ctx, other.get_one(ctx, RailCompany))

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.get_one(ctx, RailCompany).merged_attr(ctx, "name")


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Connection(ToSerializable):
    company_name: str
    line_code: str
    one_way_towards_code: str | None

    def __init__(self, ctx: RailContext, *, line: RailLine, one_way_towards: Station | None = None):
        self.set_line(ctx, line)
        self.set_one_way_towards(ctx, one_way_towards)

    @override
    class Ser(msgspec.Struct):
        line: uuid.UUID
        one_way_towards: uuid.UUID | None = None

    def ser(self, ctx: RailContext) -> Connection.Ser:
        return self.Ser(
            line=self.get_line(ctx).id, one_way_towards=None if (s := self.get_one_way_towards(ctx) is None) else s.id
        )

    def get_company(self, ctx: RailContext) -> RailCompany:
        return ctx.company(name=self.company_name)

    def set_company(self, ctx: RailContext, v: RailCompany):
        self.company_name = v.merged_attr(ctx, "name")

    def get_one_way_towards(self, ctx: RailContext) -> Station | None:
        return (
            None
            if self.one_way_towards_code is None
            else ctx.station(codes={self.one_way_towards_code}, company=self.get_company(ctx))
        )

    def set_one_way_towards(self, ctx: RailContext, v: Station | None):
        if v is None:
            self.one_way_towards_code = None
            return
        self.one_way_towards_code = v.merged_attr(ctx, "codes")[0]
        self.set_company(ctx, v.get_one(ctx, RailCompany))

    def get_line(self, ctx: RailContext) -> RailLine:
        return ctx.line(code=self.line_code, company=self.get_company(ctx))

    def set_line(self, ctx: RailContext, v: RailLine):
        self.line_code = v.merged_attr(ctx, "code")
        self.set_company(ctx, v.get_one(ctx, RailCompany))


class RailContext(_RailContext):
    @override
    class Ser(msgspec.Struct):
        rail_company: dict[uuid.UUID, RailCompany.Ser]
        rail_line: dict[uuid.UUID, RailLine.Ser]
        station: dict[uuid.UUID, Station.Ser]

    def ser(self, _=None) -> RailContext.Ser:
        return RailContext.Ser(
            rail_company={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, RailCompany)},
            rail_line={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, RailLine)},
            station={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, Station)},
        )

    def company(self, source: type[RailContext] | None = None, *, name: str, **attrs) -> RailCompany:
        for n in self.g.nodes:
            if not isinstance(n, RailCompany):
                continue
            if n.merged_attr(self, "name") == name:
                return n
        return RailCompany(self, source, name=name, **attrs)

    def line(self, source: type[RailContext] | None = None, *, code: str, company: RailCompany, **attrs) -> RailLine:
        for n in self.g.nodes:
            if not isinstance(n, RailLine):
                continue
            if n.merged_attr(self, "code") == code and n.get_one(self, RailCompany).equivalent(self, company):
                return n
        return RailLine(self, source, code=code, company=company, **attrs)

    def station(
        self, source: type[RailContext] | None = None, *, codes: set[str], company: RailCompany, **attrs
    ) -> Station:
        for n in self.g.nodes:
            if not isinstance(n, Station):
                continue
            if len(n.merged_attr(self, "codes").intersection(codes)) != 0 and n.get_one(self, RailCompany).equivalent(
                self, company
            ):
                return n
        return Station(self, source, codes=codes, company=company, **attrs)


class RailSource(RailContext, Source):
    pass
