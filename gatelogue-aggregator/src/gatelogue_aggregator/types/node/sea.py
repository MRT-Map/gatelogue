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


class SeaSource(BaseContext, Source):
    pass


class SeaCompany(gt.SeaCompany, Node[SeaSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (SeaLine, SeaStop)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SeaSource,
        *,
        name: str,
        lines: Iterable[SeaLine] | None = None,
        stops: Iterable[SeaStop] | None = None,
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
    def str_ctx(self, ctx: SeaSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: SeaSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: SeaSource, other: Self):
        self.local = self.local or other.local

    @override
    def merge_key(self, ctx: SeaSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        self.name = str(self.name).strip()

    @override
    def export(self, ctx: SeaSource) -> gt.SeaCompany:
        return gt.SeaCompany(
            **self._as_dict(ctx),
        )

    @override
    def _as_dict(self, ctx: SeaSource) -> dict:
        return super()._as_dict(ctx) | {
            "lines": self.get_all_id(ctx, SeaLine),
            "stops": self.get_all_id(ctx, SeaStop),
        }

    @override
    def ref(self, ctx: SeaSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(SeaCompany, name=self.name)


class SeaLine(gt.SeaLine, Node[SeaSource], kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (SeaCompany, SeaStop)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SeaSource,
        *,
        code: str,
        company: SeaCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: gt.SeaMode | None = None,
        ref_stop: SeaStop | None = None,
    ):
        self = super().new(ctx, code=code)
        self.connect_one(ctx, company)
        if name is not None:
            self.name = ctx.source(name)
        if colour is not None:
            self.colour = ctx.source(colour)
        if mode is not None:
            self.mode = ctx.source(mode)
        if ref_stop is not None:
            self.connect_one(ctx, ref_stop)
        return self

    @override
    def str_ctx(self, ctx: SeaSource) -> str:
        code = self.code
        company = self.get_one(ctx, SeaCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: SeaSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, SeaCompany).equivalent(ctx, other.get_one(ctx, SeaCompany))

    @override
    def merge_attrs(self, ctx: SeaSource, other: Self):
        self._merge_sourced(ctx, other, "name")
        self._merge_sourced(ctx, other, "colour")
        self._merge_sourced(ctx, other, "mode")

    @override
    def merge_key(self, ctx: SeaSource) -> str:
        return self.code

    @override
    def sanitise_strings(self):
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.colour is not None:
            self.colour.v = str(self.colour.v).strip()

    @override
    def export(self, ctx: SeaSource) -> gt.SeaLine:
        return gt.SeaLine(
            **self._as_dict(ctx),
        )

    @override
    def _as_dict(self, ctx: SeaSource) -> dict:
        return super()._as_dict(ctx) | {
            "company": self.get_one_id(ctx, SeaCompany),
            "ref_stop": self.get_one_id(ctx, SeaStop),
        }

    @override
    def ref(self, ctx: SeaSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(SeaLine, code=self.code, company=self.get_one(ctx, SeaCompany).name)


class SeaStop(gt.SeaStop, LocatedNode[SeaSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (SeaStop, SeaLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (SeaCompany,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SeaSource,
        *,
        codes: set[str],
        company: SeaCompany,
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
    def str_ctx(self, ctx: SeaSource) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, SeaCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: SeaSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, SeaCompany).equivalent(
            ctx, other.get_one(ctx, SeaCompany)
        )

    @override
    def merge_attrs(self, ctx: SeaSource, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: SeaSource) -> str:
        return self.get_one(ctx, SeaCompany).name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.codes = {str(a).strip() for a in self.codes}
        if self.name is not None:
            self.name.v = str(self.name.v).strip()

    @override
    def export(self, ctx: SeaSource) -> gt.SeaStop:
        return gt.SeaStop(
            **self._as_dict(ctx),
        )

    @override
    def _as_dict(self, ctx: SeaSource) -> dict:
        return super()._as_dict(ctx) | {
            "company": self.get_one_id(ctx, SeaCompany),
            "connections": {
                node.i: [a.export(ctx) for a in self.get_edges(ctx, node, SeaConnection)]
                for node in self.get_all(ctx, SeaStop)
            },
        }

    @override
    def ref(self, ctx: SeaSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(SeaStop, codes=self.codes, company=self.get_one(ctx, SeaCompany).name)


class SeaConnection(Connection[SeaSource, SeaLine]):
    pass


class SeaLineBuilder(LineBuilder[SeaSource, SeaLine, SeaStop]):
    CnT = SeaConnection
