from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self, override

import gatelogue_types as gt

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef
from gatelogue_aggregator.types.source import Source

if TYPE_CHECKING:
    from collections.abc import Iterable


class BusSource(BaseContext, Source):
    pass


class BusCompany(gt.BusCompany, Node[BusSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (BusLine, BusStop)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: BusSource,
        *,
        name: str,
        lines: Iterable[BusLine] | None = None,
        stops: Iterable[BusStop] | None = None,
        local: bool = False,
    ):
        self = super().new(ctx, name=name, local=local)
        if lines is not None:
            for line in lines:
                self.connect(ctx, line)
        if stops is not None:
            for stop in stops:
                self.connect(ctx, stop)
        return self

    @override
    def str_ctx(self, ctx: BusSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: BusSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: BusSource, other: Self):
        self.local = self.local or other.local

    @override
    def merge_key(self, ctx: BusSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        self.name = str(self.name).strip()

    @override
    def export(self, ctx: BusSource) -> gt.BusCompany:
        return gt.BusCompany(**self._as_dict(ctx))

    @override
    def _as_dict(self, ctx: BusSource) -> dict:
        return super()._as_dict(ctx) | {
            "lines": self.get_all_id(ctx, BusLine),
            "stops": self.get_all_id(ctx, BusStop),
        }

    @override
    def ref(self, ctx: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusCompany, name=self.name)


class BusLine(gt.BusLine, Node[BusSource], kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (BusCompany, BusStop)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: BusSource,
        *,
        code: str,
        company: BusCompany,
        name: str | None = None,
        colour: str | None = None,
        ref_stop: BusStop | None = None,
    ):
        self = super().new(ctx, code=code)
        self.connect_one(ctx, company)
        if name is not None:
            self.name = ctx.source(name)
        if colour is not None:
            self.colour = ctx.source(colour)
        if ref_stop is not None:
            self.connect_one(ctx, ref_stop)
        return self

    @override
    def str_ctx(self, ctx: BusSource) -> str:
        code = self.code
        company = self.get_one(ctx, BusCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: BusSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, BusCompany).equivalent(ctx, other.get_one(ctx, BusCompany))

    @override
    def merge_attrs(self, ctx: BusSource, other: Self):
        self._merge_sourced(ctx, other, "name")
        self._merge_sourced(ctx, other, "colour")

    @override
    def merge_key(self, ctx: BusSource) -> str:
        return self.code

    @override
    def sanitise_strings(self):
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.colour is not None:
            self.colour.v = str(self.colour.v).strip()

    @override
    def export(self, ctx: BusSource) -> gt.BusLine:
        return gt.BusLine(**self._as_dict(ctx))

    @override
    def _as_dict(self, ctx: BusSource) -> dict:
        return super()._as_dict(ctx) | {
            "company": self.get_one_id(ctx, BusCompany),
            "ref_stop": self.get_one_id(ctx, BusStop),
        }

    @override
    def ref(self, ctx: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusLine, code=self.code, company=self.get_one(ctx, BusCompany).name)


class BusStop(gt.BusStop, LocatedNode[BusSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (BusStop, BusLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (BusCompany,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: BusSource,
        *,
        codes: set[str],
        company: BusCompany,
        name: str | None = None,
        world: gt.World | None = None,
        coordinates: tuple[float, float] | None = None,
    ):
        self = super().new(ctx, world=world, coordinates=coordinates, codes=codes)
        self.connect_one(ctx, company)
        if name is not None:
            self.name = ctx.source(name)
        return self

    @override
    def str_ctx(self, ctx: BusSource) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, BusCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: BusSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, BusCompany).equivalent(
            ctx, other.get_one(ctx, BusCompany)
        )

    @override
    def merge_attrs(self, ctx: BusSource, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: BusSource) -> str:
        return self.get_one(ctx, BusCompany).name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.codes = {str(a).strip() for a in self.codes}
        if self.name is not None:
            self.name.v = str(self.name.v).strip()

    @override
    def export(self, ctx: BusSource) -> gt.BusStop:
        return gt.BusStop(
            **self._as_dict(ctx),
        )

    @override
    def _as_dict(self, ctx: BusSource) -> dict:
        return super()._as_dict(ctx) | {
            "company": self.get_one_id(ctx, BusCompany),
            "connections": {
                node.i: [a.export(ctx) for a in self.get_edges(ctx, node, BusConnection)]
                for node in self.get_all(ctx, BusStop)
            },
        }

    @override
    def ref(self, ctx: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusStop, codes=self.codes, company=self.get_one(ctx, BusCompany).name)


class BusConnection(Connection[BusSource, BusLine]):
    pass


class BusLineBuilder(LineBuilder[BusSource, BusLine, BusStop]):
    CnT = BusConnection
