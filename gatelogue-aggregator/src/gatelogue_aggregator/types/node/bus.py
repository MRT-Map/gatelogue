from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Self, override

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Source, Sourced
from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node

if TYPE_CHECKING:
    import uuid
    from collections.abc import Container


class _BusContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class BusCompany(Node[_BusContext]):
    acceptable_list_node_types = lambda: (BusLine, BusStop)  # noqa: E731

    @override
    def __init__(self, ctx: BusContext, source: type[BusContext] | None = None, *, name: str, **attrs):
        super().__init__(ctx, source, name=name, **attrs)

    @override
    def str_ctx(self, ctx: BusContext, filter_: Container[str] | None = None) -> str:
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
        import uuid

        name: str
        lines: list[Sourced.Ser[uuid.UUID]]
        stops: list[Sourced.Ser[uuid.UUID]]

    def ser(self, ctx: BusContext) -> BusCompany.Ser:
        return self.Ser(
            **self.merged_attrs(ctx), lines=self.get_all_ser(ctx, BusLine), stops=self.get_all_ser(ctx, BusStop)
        )

    @override
    def equivalent(self, ctx: BusContext, other: Self) -> bool:
        return self.merged_attr(ctx, "name") == other.merged_attr(ctx, "name")

    @override
    def merge_key(self, ctx: BusContext) -> str:
        return self.merged_attr(ctx, "name")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class BusLine(Node[_BusContext]):
    acceptable_single_node_types = lambda: (BusCompany, BusStop)  # noqa: E731

    @override
    def __init__(
        self, ctx: BusContext, source: type[BusContext] | None = None, *, code: str, company: BusCompany, **attrs
    ):
        super().__init__(ctx, source, code=code, **attrs)
        self.connect_one(ctx, company)

    @override
    def str_ctx(self, ctx: BusContext, filter_: Container[str] | None = None) -> str:
        code = self.merged_attr(ctx, "code")
        company = self.get_one(ctx, BusCompany).merged_attr(ctx, "name")
        return f"{company} {code}"

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(Node.Attrs):
        code: str
        name: str | None = None
        colour: str | None = None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "code":
                return v
            if k in ("name", "colour"):
                return Sourced(v).source(source)
            raise NotImplementedError

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            self.sourced_merge(source, existing, "name")
            self.sourced_merge(source, existing, "colour")

    @override
    class Ser(Node.Ser, kw_only=True):
        import uuid

        code: str
        company: Sourced.Ser[uuid.UUID]
        ref_stop: Sourced.Ser[uuid.UUID]
        name: Sourced.Ser[str] | None
        colour: Sourced.Ser[str] | None

    def ser(self, ctx: BusContext) -> BusLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, BusCompany),
            ref_stop=self.get_one_ser(ctx, BusStop),
        )

    @override
    def equivalent(self, ctx: BusContext, other: Self) -> bool:
        return self.merged_attr(ctx, "code") == other.merged_attr(ctx, "code") and self.get_one(
            ctx, BusCompany
        ).equivalent(ctx, other.get_one(ctx, BusCompany))

    @override
    def merge_key(self, ctx: BusContext) -> str:
        return self.merged_attr(ctx, "code")


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class BusStop(LocatedNode[_BusContext]):
    acceptable_list_node_types = lambda: (BusStop, BusLine, LocatedNode)  # noqa: E731
    acceptable_single_node_types = lambda: (BusCompany,)  # noqa: E731

    @override
    def __init__(
        self,
        ctx: BusContext,
        source: type[BusContext] | None = None,
        *,
        codes: set[str],
        company: BusCompany,
        **attrs,
    ):
        super().__init__(ctx, source, codes=codes, **attrs)
        self.connect_one(ctx, company)

    @override
    def str_ctx(self, ctx: BusContext, filter_: Container[str] | None = None) -> str:
        code = "/".join(self.merged_attr(ctx, "codes")) if (code := self.merged_attr(ctx, "name")) is None else code.v
        company = self.get_one(ctx, BusCompany).merged_attr(ctx, "name")
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
        import uuid

        codes: set[str]
        company: Sourced.Ser[uuid.UUID]
        connections: dict[uuid.UUID, list[Sourced.Ser[BusConnection.Ser]]]
        name: Sourced.Ser[str] | None

    def ser(self, ctx: BusContext) -> BusLine.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            company=self.get_one_ser(ctx, BusCompany),
            connections={n.id: self.get_edges_ser(ctx, n, BusConnection) for n in self.get_all(ctx, BusStop)},
            proximity=self.get_proximity_ser(ctx),
        )

    @override
    def equivalent(self, ctx: BusContext, other: Self) -> bool:
        return len(self.merged_attr(ctx, "codes").intersection(other.merged_attr(ctx, "codes"))) != 0 and self.get_one(
            ctx, BusCompany
        ).equivalent(ctx, other.get_one(ctx, BusCompany))

    @override
    def merge_key(self, ctx: BusContext) -> str:
        return self.get_one(ctx, BusCompany).merged_attr(ctx, "name")


class BusConnection(Connection[_BusContext, BusCompany, BusLine, BusStop]):
    CT = BusCompany
    company_fn = lambda ctx: ctx.bus_company  # noqa: E731
    line_fn = lambda ctx: ctx.bus_line  # noqa: E731
    station_fn = lambda ctx: ctx.bus_stop  # noqa: E731


class BusLineBuilder(LineBuilder[_BusContext, BusLine, BusStop]):
    CnT = BusConnection


class BusContext(_BusContext):
    @override
    class Ser(msgspec.Struct, kw_only=True):
        import uuid

        company: dict[uuid.UUID, BusCompany.Ser]
        line: dict[uuid.UUID, BusLine.Ser]
        stop: dict[uuid.UUID, BusStop.Ser]

    def ser(self, _=None) -> BusContext.Ser:
        return BusContext.Ser(
            company={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, BusCompany)},
            line={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, BusLine)},
            stop={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, BusStop)},
        )

    def bus_company(self, source: type[BusContext] | None = None, *, name: str, **attrs) -> BusCompany:
        for n in self.g.nodes:
            if not isinstance(n, BusCompany):
                continue
            if n.merged_attr(self, "name") == name:
                return n
        return BusCompany(self, source, name=name, **attrs)

    def bus_line(self, source: type[BusContext] | None = None, *, code: str, company: BusCompany, **attrs) -> BusLine:
        for n in self.g.nodes:
            if not isinstance(n, BusLine):
                continue
            if n.merged_attr(self, "code") == code and n.get_one(self, BusCompany).equivalent(self, company):
                return n
        return BusLine(self, source, code=code, company=company, **attrs)

    def bus_stop(
        self, source: type[BusContext] | None = None, *, codes: set[str], company: BusCompany, **attrs
    ) -> BusStop:
        for n in self.g.nodes:
            if not isinstance(n, BusStop):
                continue
            if len(n.merged_attr(self, "codes").intersection(codes)) != 0 and n.get_one(self, BusCompany).equivalent(
                self, company
            ):
                return n
        return BusStop(self, source, codes=codes, company=company, **attrs)


class BusSource(BusContext, Source):
    pass
