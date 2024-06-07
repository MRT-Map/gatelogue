from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Literal, Self, override

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Source, Sourced
from gatelogue_aggregator.types.connections import Connection, Proximity
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node

if TYPE_CHECKING:
    import uuid
    from collections.abc import Container


class _SeaContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class SeaCompany(Node[_SeaContext]):
    acceptable_list_node_types = lambda: (SeaLine, SeaStop)  # noqa: E731

    @override
    def __init__(self, ctx: SeaContext, source: type[SeaContext] | None = None, *, name: str, **attrs):
        super().__init__(ctx, source, name=name, **attrs)

    @override
    def str_ctx(self, ctx: SeaContext, filter_: Container[str] | None = None) -> str:
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
        stops: list[Sourced.Ser[uuid.UUID]]

    def ser(self, ctx: SeaContext) -> SeaCompany.Ser:
        return self.Ser(
            **self.merged_attrs(ctx), lines=self.get_all_ser(ctx, SeaLine), stops=self.get_all_ser(ctx, SeaStop)
        )

    @override
    def equivalent(self, ctx: SeaContext, other: Self) -> bool:
        return self.merged_attr(ctx, "name") == other.merged_attr(ctx, "name")

    @override
    def merge_key(self, ctx: SeaContext) -> str:
        return self.merged_attr(ctx, "name")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class SeaLine(Node[_SeaContext]):
    acceptable_single_node_types = lambda: (SeaCompany, SeaStop)  # noqa: E731

    @override
    def __init__(
        self, ctx: SeaContext, source: type[SeaContext] | None = None, *, code: str, company: SeaCompany, **attrs
    ):
        super().__init__(ctx, source, code=code, **attrs)
        self.connect_one(ctx, company)

    @override
    def str_ctx(self, ctx: SeaContext, filter_: Container[str] | None = None) -> str:
        code = self.merged_attr(ctx, "code")
        company = self.get_one(ctx, SeaCompany).merged_attr(ctx, "name")
        return f"{company} {code}"

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str
        mode: Literal["ferry", "cruise"] | None = None
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
        ref_stop: Sourced.Ser[uuid.UUID]
        mode: Sourced.Ser[Literal["ferry", "cruise"]] | None
        name: Sourced.Ser[str] | None
        colour: Sourced.Ser[str] | None

    def ser(self, ctx: SeaContext) -> SeaLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, SeaCompany),
            ref_stop=self.get_one_ser(ctx, SeaStop),
        )

    @override
    def equivalent(self, ctx: SeaContext, other: Self) -> bool:
        return self.merged_attr(ctx, "code") == other.merged_attr(ctx, "code") and self.get_one(
            ctx, SeaCompany
        ).equivalent(ctx, other.get_one(ctx, SeaCompany))

    @override
    def merge_key(self, ctx: SeaContext) -> str:
        return self.merged_attr(ctx, "code")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class SeaStop(LocatedNode[_SeaContext]):
    acceptable_list_node_types = lambda: (SeaStop, SeaLine, LocatedNode)  # noqa: E731
    acceptable_single_node_types = lambda: (SeaCompany,)  # noqa: E731

    @override
    def __init__(
        self,
        ctx: SeaContext,
        source: type[SeaContext] | None = None,
        *,
        codes: set[str],
        company: SeaCompany,
        **attrs,
    ):
        super().__init__(ctx, source, codes=codes, **attrs)
        self.connect_one(ctx, company)

    @override
    def str_ctx(self, ctx: SeaContext, filter_: Container[str] | None = None) -> str:
        code = "/".join(self.merged_attr(ctx, "codes")) if (code := self.merged_attr(ctx, "name")) is None else code.v
        company = self.get_one(ctx, SeaCompany).merged_attr(ctx, "name")
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
        connections: dict[uuid.UUID, list[Sourced.Ser[SeaConnection]]]
        proximity: dict[uuid.UUID, str]
        name: Sourced.Ser[str] | None

    def ser(self, ctx: SeaContext) -> SeaLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, SeaCompany),
            connections={n.id: self.get_edges_ser(ctx, n, SeaConnection) for n in self.get_all(ctx, SeaStop)},
            proximity={
                n.id: type(n).__name__.lower()
                for n in self.get_all(ctx, LocatedNode)
                if len(self.get_edges_ser(ctx, n, Proximity)) != 0
            },
        )

    @override
    def equivalent(self, ctx: SeaContext, other: Self) -> bool:
        return len(self.merged_attr(ctx, "codes").intersection(other.merged_attr(ctx, "codes"))) != 0 and self.get_one(
            ctx, SeaCompany
        ).equivalent(ctx, other.get_one(ctx, SeaCompany))

    @override
    def merge_key(self, ctx: SeaContext) -> str:
        return self.get_one(ctx, SeaCompany).merged_attr(ctx, "name")


class SeaConnection(Connection[_SeaContext, SeaCompany, SeaLine, SeaStop]):
    CT = SeaCompany
    company_fn = lambda ctx: ctx.sea_company  # noqa: E731
    line_fn = lambda ctx: ctx.sea_line  # noqa: E731
    station_fn = lambda ctx: ctx.sea_stop  # noqa: E731


class SeaLineBuilder(LineBuilder[_SeaContext, SeaLine, SeaStop]):
    CnT = SeaConnection


class SeaContext(_SeaContext):
    @override
    class Ser(msgspec.Struct, kw_only=True):
        sea_company: dict[uuid.UUID, SeaCompany.Ser]
        sea_line: dict[uuid.UUID, SeaLine.Ser]
        sea_stop: dict[uuid.UUID, SeaStop.Ser]

    def ser(self, _=None) -> SeaContext.Ser:
        return SeaContext.Ser(
            sea_company={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, SeaCompany)},
            sea_line={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, SeaLine)},
            sea_stop={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, SeaStop)},
        )

    def sea_company(self, source: type[SeaContext] | None = None, *, name: str, **attrs) -> SeaCompany:
        for n in self.g.nodes:
            if not isinstance(n, SeaCompany):
                continue
            if n.merged_attr(self, "name") == name:
                return n
        return SeaCompany(self, source, name=name, **attrs)

    def sea_line(self, source: type[SeaContext] | None = None, *, code: str, company: SeaCompany, **attrs) -> SeaLine:
        for n in self.g.nodes:
            if not isinstance(n, SeaLine):
                continue
            if n.merged_attr(self, "code") == code and n.get_one(self, SeaCompany).equivalent(self, company):
                return n
        return SeaLine(self, source, code=code, company=company, **attrs)

    def sea_stop(
        self, source: type[SeaContext] | None = None, *, codes: set[str], company: SeaCompany, **attrs
    ) -> SeaStop:
        for n in self.g.nodes:
            if not isinstance(n, SeaStop):
                continue
            if len(n.merged_attr(self, "codes").intersection(codes)) != 0 and n.get_one(self, SeaCompany).equivalent(
                self, company
            ):
                return n
        return SeaStop(self, source, codes=codes, company=company, **attrs)


class SeaSource(SeaContext, Source):
    pass
