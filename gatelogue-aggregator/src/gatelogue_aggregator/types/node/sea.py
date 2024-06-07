from __future__ import annotations

import dataclasses
import itertools
from typing import TYPE_CHECKING, Any, Literal, Self, override

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Proximity, Source, Sourced, ToSerializable
from gatelogue_aggregator.types.node.base import Node, LocatedNode
from gatelogue_aggregator.types.node.rail import RailDirection

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
    def attrs(self, ctx: SeaContext, source: type[SeaContext] | None = None) -> SeaCompany.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: SeaContext) -> dict[Source, SeaCompany.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
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
    def attrs(self, ctx: SeaContext, source: type[SeaContext] | None = None) -> SeaLine.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: SeaContext) -> dict[Source, SeaLine.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        code: str
        company: Sourced.Ser[uuid.UUID]
        ref_stop: Sourced.Ser[uuid.UUID]
        mode: Sourced.Ser[Literal["ferry", "cruise"]] | None = None
        name: Sourced.Ser[str] | None = None
        colour: Sourced.Ser[str] | None = None

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
    def attrs(self, ctx: SeaContext, source: type[SeaContext] | None = None) -> SeaStop.Attrs | None:
        return super().attrs(ctx, source)

    @override
    def all_attrs(self, ctx: SeaContext) -> dict[Source, SeaStop.Attrs]:
        return super().all_attrs(ctx)

    @override
    class Ser(msgspec.Struct):
        codes: set[str]
        company: Sourced.Ser[uuid.UUID]
        connections: dict[uuid.UUID, list[Sourced.Ser[SeaConnection]]]
        proximity: dict[uuid.UUID, str]
        name: Sourced.Ser[str] | None = None
        world: Sourced.Ser[Literal["New", "Old"]] | None = None
        coordinates: Sourced.Ser[tuple[int, int]] | None = None

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


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class SeaDirection(RailDirection):
    pass


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class SeaConnection(ToSerializable):
    company_name: str
    line_code: str
    direction: SeaDirection | None = None

    def __init__(self, ctx: SeaContext, *, line: SeaLine, direction: SeaDirection | None = None):
        self.set_line(ctx, line)
        self.direction = direction

    @override
    class Ser(msgspec.Struct):
        line: uuid.UUID
        direction: SeaDirection.Ser | None = None

    def ser(self, ctx: SeaContext) -> SeaConnection.Ser:
        return self.Ser(
            line=self.get_line(ctx).id,
            direction=SeaDirection.Ser(
                forward_towards_code=self.get_direction_forward_towards(ctx),
                forward_direction_label=self.direction.forward_direction_label,
                backward_direction_label=self.direction.backward_direction_label,
                one_way=self.direction.one_way,
            )
            if self.direction is not None
            else None,
        )

    def get_company(self, ctx: SeaContext) -> SeaCompany:
        return ctx.sea_company(name=self.company_name)

    def set_company(self, ctx: SeaContext, v: SeaCompany):
        self.company_name = v.merged_attr(ctx, "name")

    def get_direction_forward_towards(self, ctx: SeaContext) -> SeaStop | None:
        return (
            None
            if self.direction is None
            else ctx.sea_stop(codes={self.direction.forward_towards_code}, company=self.get_company(ctx))
        )

    def set_direction_forward_towards(self, ctx: SeaContext, v: SeaStop):
        self.direction.forward_towards_code = v.merged_attr(ctx, "codes")[0]
        self.set_company(ctx, v.get_one(ctx, SeaCompany))

    def get_line(self, ctx: SeaContext) -> SeaLine:
        return ctx.sea_line(code=self.line_code, company=self.get_company(ctx))

    def set_line(self, ctx: SeaContext, v: SeaLine):
        self.line_code = v.merged_attr(ctx, "code")
        self.set_company(ctx, v.get_one(ctx, SeaCompany))


class SeaLineBuilder:
    def __init__(self, ctx: SeaContext, line: SeaLine):
        self.ctx = ctx
        self.line = line

    def connect(
        self,
        *stops: SeaStop,
        forward_label: str | None = None,
        backward_label: str | None = None,
        one_way: bool = False,
    ):
        if len(stops) == 0:
            return
        self.line.connect_one(self.ctx, stops[0])
        forward_label = forward_label or "towards " + (
            a.v
            if (a := stops[-1].merged_attr(self.ctx, "name")) is not None
            else next(iter(stops[-1].merged_attr(self.ctx, "codes")))
        )
        backward_label = backward_label or "towards " + (
            a.v
            if (a := stops[0].merged_attr(self.ctx, "name")) is not None
            else next(iter(stops[0].merged_attr(self.ctx, "codes")))
        )
        for s1, s2 in itertools.pairwise(stops):
            s1: SeaStop
            s2: SeaStop
            s1.connect(
                self.ctx,
                s2,
                value=SeaConnection(
                    self.ctx,
                    line=self.line,
                    direction=SeaDirection(
                        forward_towards_code=next(iter(s2.merged_attr(self.ctx, "codes", set))),
                        forward_direction_label=forward_label,
                        backward_direction_label=backward_label,
                        one_way=one_way,
                    ),
                ),
            )

    def circle(
        self,
        *stops: SeaStop,
        forward_label: str | None = None,
        backward_label: str | None = None,
        one_way: bool = False,
    ):
        if len(stops) == 0:
            return
        self.connect(*stops, stops[0], forward_label=forward_label, backward_label=backward_label, one_way=one_way)


class SeaContext(_SeaContext):
    @override
    class Ser(msgspec.Struct):
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
