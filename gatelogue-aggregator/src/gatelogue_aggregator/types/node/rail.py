from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Literal, Self, override

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Source, Sourced
from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node

if TYPE_CHECKING:
    import uuid
    from collections.abc import Container


class _RailContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailCompany(Node[_RailContext]):
    acceptable_list_node_types = lambda: (RailLine, RailStation)  # noqa: E731

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
    class Ser(Node.Ser, kw_only=True):
        name: str
        lines: list[Sourced.Ser[uuid.UUID]]
        stations: list[Sourced.Ser[uuid.UUID]]

    def ser(self, ctx: RailContext) -> RailCompany.Ser:
        return self.Ser(
            **self.merged_attrs(ctx), lines=self.get_all_ser(ctx, RailLine), stations=self.get_all_ser(ctx, RailStation)
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.merged_attr(ctx, "name") == other.merged_attr(ctx, "name")

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.merged_attr(ctx, "name")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailLine(Node[_RailContext]):
    acceptable_single_node_types = lambda: (RailCompany, RailStation)  # noqa: E731

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
        colour: str | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            if k in ("name", "mode", "colour"):
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "name")
            self.sourced_merge(source, existing, "mode")
            self.sourced_merge(source, existing, "colour")

    @override
    class Ser(Node.Ser, kw_only=True):
        code: str
        company: Sourced.Ser[uuid.UUID]
        ref_station: Sourced.Ser[uuid.UUID]
        mode: Sourced.Ser[Literal["warp", "cart", "traincart", "vehicles"]] | None = None
        name: Sourced.Ser[str] | None = None
        colour: Sourced.Ser[str] | None = None

    def ser(self, ctx: RailContext) -> RailLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, RailCompany),
            ref_station=self.get_one_ser(ctx, RailStation),
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.merged_attr(ctx, "code") == other.merged_attr(ctx, "code") and self.get_one(
            ctx, RailCompany
        ).equivalent(ctx, other.get_one(ctx, RailCompany))

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.merged_attr(ctx, "code")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailStation(LocatedNode[_RailContext]):
    acceptable_list_node_types = lambda: (RailStation, RailLine, LocatedNode)  # noqa: E731
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
    class Attrs(LocatedNode.Attrs):
        codes: set[str]
        name: str | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "codes":
                return v
            if k == "name":
                return Sourced(v).source(source)
            return LocatedNode.Attrs.prepare_merge(source, k, v)

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            super().merge_into(source, existing)
            if "codes" in existing:
                existing["codes"].update(self.codes)
            self.sourced_merge(source, existing, "name")

    @override
    class Ser(LocatedNode.Ser, kw_only=True):
        codes: set[str]
        company: Sourced.Ser[uuid.UUID]
        connections: dict[uuid.UUID, list[Sourced.Ser[RailConnection]]]
        name: Sourced.Ser[str] | None

    def ser(self, ctx: RailContext) -> RailLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, RailCompany),
            connections={n.id: self.get_edges_ser(ctx, n, RailConnection) for n in self.get_all(ctx, RailStation)},
            proximity=self.get_proximity_ser(ctx),
        )

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return len(self.merged_attr(ctx, "codes").intersection(other.merged_attr(ctx, "codes"))) != 0 and self.get_one(
            ctx, RailCompany
        ).equivalent(ctx, other.get_one(ctx, RailCompany))

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.get_one(ctx, RailCompany).merged_attr(ctx, "name")


class RailConnection(Connection[_RailContext, RailCompany, RailLine, RailStation]):
    CT = RailCompany
    company_fn = lambda ctx: ctx.rail_company  # noqa: E731
    line_fn = lambda ctx: ctx.rail_line  # noqa: E731
    station_fn = lambda ctx: ctx.rail_station  # noqa: E731


class RailLineBuilder(LineBuilder[_RailContext, RailLine, RailStation]):
    CnT = RailConnection


class RailContext(_RailContext):
    @override
    class Ser(msgspec.Struct, kw_only=True):
        company: dict[uuid.UUID, RailCompany.Ser]
        line: dict[uuid.UUID, RailLine.Ser]
        station: dict[uuid.UUID, RailStation.Ser]

    def ser(self, _=None) -> RailContext.Ser:
        return RailContext.Ser(
            company={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, RailCompany)},
            line={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, RailLine)},
            station={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, RailStation)},
        )

    def rail_company(self, source: type[RailContext] | None = None, *, name: str, **attrs) -> RailCompany:
        for n in self.g.nodes:
            if not isinstance(n, RailCompany):
                continue
            if n.merged_attr(self, "name") == name:
                return n
        return RailCompany(self, source, name=name, **attrs)

    def rail_line(
        self, source: type[RailContext] | None = None, *, code: str, company: RailCompany, **attrs
    ) -> RailLine:
        for n in self.g.nodes:
            if not isinstance(n, RailLine):
                continue
            if n.merged_attr(self, "code") == code and n.get_one(self, RailCompany).equivalent(self, company):
                return n
        return RailLine(self, source, code=code, company=company, **attrs)

    def rail_station(
        self, source: type[RailContext] | None = None, *, codes: set[str], company: RailCompany, **attrs
    ) -> RailStation:
        for n in self.g.nodes:
            if not isinstance(n, RailStation):
                continue
            if len(n.merged_attr(self, "codes").intersection(codes)) != 0 and n.get_one(self, RailCompany).equivalent(
                self, company
            ):
                return n
        return RailStation(self, source, codes=codes, company=company, **attrs)


class RailSource(RailContext, Source):
    pass
