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


class RailSource(BaseContext, Source):
    pass


class RailCompany(gt.RailCompany, Node[RailSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (RailLine, RailStation)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: RailSource,
        *,
        name: str,
        lines: Iterable[RailLine] | None = None,
        stations: Iterable[RailStation] | None = None,
        local: bool = False,
    ):
        self = super().new(ctx, name=name, local=local)
        if lines is not None:
            for line in lines:
                self.connect(ctx, line)
        if stations is not None:
            for station in stations:
                self.connect(ctx, station)
        return self

    @override
    def str_ctx(self, ctx: RailSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: RailSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: RailSource, other: Self):
        self.local = self.local or other.local

    @override
    def merge_key(self, ctx: RailSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        self.name = str(self.name).strip()

    @override
    def export(self, ctx: RailSource) -> gt.RailCompany:
        return gt.RailCompany(
            **self._as_dict(ctx),
        )

    @override
    def _as_dict(self, ctx: RailSource) -> dict:
        return super()._as_dict(ctx) | {
            "lines": self.get_all_id(ctx, RailLine),
            "stations": self.get_all_id(ctx, RailStation),
        }

    @override
    def ref(self, ctx: RailSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(RailCompany, name=self.name)


class RailLine(gt.RailLine, Node[RailSource], kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (RailCompany, RailStation)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: RailSource,
        *,
        code: str,
        company: RailCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: gt.RailMode | None = None,
        ref_station: RailStation | None = None,
    ):
        self = super().new(ctx, code=code)
        self.connect_one(ctx, company)
        if name is not None:
            self.name = ctx.source(name)
        if colour is not None:
            self.colour = ctx.source(colour)
        if mode is not None:
            self.mode = ctx.source(mode)
        if ref_station is not None:
            self.connect_one(ctx, ref_station)
        return self

    @override
    def str_ctx(self, ctx: RailSource) -> str:
        code = self.code
        company = self.get_one(ctx, RailCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: RailSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, RailCompany).equivalent(
            ctx, other.get_one(ctx, RailCompany)
        )

    @override
    def merge_attrs(self, ctx: RailSource, other: Self):
        self._merge_sourced(ctx, other, "name")
        self._merge_sourced(ctx, other, "colour")
        self._merge_sourced(ctx, other, "mode")

    @override
    def merge_key(self, ctx: RailSource) -> str:
        return self.code

    @override
    def sanitise_strings(self):
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.colour is not None:
            self.colour.v = str(self.colour.v).strip()
        if self.mode is not None:
            self.mode.v = str(self.mode.v).strip()

    @override
    def export(self, ctx: RailSource) -> gt.RailLine:
        return gt.RailLine(
            **self._as_dict(ctx),
        )

    @override
    def _as_dict(self, ctx: RailSource) -> dict:
        return super()._as_dict(ctx) | {
            "company": self.get_one_id(ctx, RailCompany),
            "ref_station": self.get_one_id(ctx, RailStation),
        }

    @override
    def ref(self, ctx: RailSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(RailLine, code=self.code, company=self.get_one(ctx, RailCompany).name)


class RailStation(gt.RailStation, LocatedNode[RailSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (RailStation, RailLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (RailCompany,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: RailSource,
        *,
        codes: set[str],
        company: RailCompany,
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
    def str_ctx(self, ctx: RailSource) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, RailCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: RailSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, RailCompany).equivalent(
            ctx, other.get_one(ctx, RailCompany)
        )

    @override
    def merge_attrs(self, ctx: RailSource, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: RailSource) -> str:
        return self.get_one(ctx, RailCompany).name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.codes = {str(a).strip() for a in self.codes}
        if self.name is not None:
            self.name.v = str(self.name.v).strip()

    @override
    def export(self, ctx: RailSource) -> gt.RailStation:
        return gt.RailStation(
            **self._as_dict(ctx),
        )

    @override
    def _as_dict(self, ctx: RailSource) -> dict:
        return super()._as_dict(ctx) | {
            "company": self.get_one_id(ctx, RailCompany),
            "connections": {
                node.i: [a.export(ctx) for a in self.get_edges(ctx, node, RailConnection)]
                for node in self.get_all(ctx, RailStation, RailConnection)
            },
        }

    @override
    def ref(self, ctx: RailSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(RailStation, codes=self.codes, company=self.get_one(ctx, RailCompany).name)


class RailConnection(Connection[RailSource, RailLine]):
    pass


class RailLineBuilder(LineBuilder[RailSource, RailLine, RailStation]):
    CnT = RailConnection
