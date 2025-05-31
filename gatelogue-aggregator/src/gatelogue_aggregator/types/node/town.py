from __future__ import annotations

from typing import ClassVar, Self, override

import gatelogue_types as gt

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.node.base import LocatedNode, NodeRef
from gatelogue_aggregator.types.source import Source


class TownSource(BaseContext, Source):
    pass


class Town(gt.Town, LocatedNode[TownSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (LocatedNode,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: TownSource,
        *,
        name: str,
        rank: gt.Rank,
        mayor: str,
        deputy_mayor: str | None,
        world: gt.World | None = None,
        coordinates: tuple[float, float] | None = None,
    ):
        return super().new(
            ctx,
            world=world,
            coordinates=coordinates,
            name=name,
            rank=ctx.source(rank),
            mayor=ctx.source(mayor),
            deputy_mayor=ctx.source(deputy_mayor),
        )

    @override
    def str_ctx(self, ctx: TownSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: TownSource, other: Self) -> bool:
        if self.world.v is not None and other.world.v is not None and self.world.v != other.world.v:
            return False
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: TownSource, other: Self):
        super().merge_attrs(ctx, other)
        self._merge_sourced(ctx, other, "rank")
        self._merge_sourced(ctx, other, "mayor")
        self._merge_sourced(ctx, other, "deputy_mayor")

    @override
    def merge_key(self, ctx: TownSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.name = str(self.name).strip()
        self.rank.v = str(self.rank.v).strip()
        self.mayor.v = str(self.mayor.v).strip()
        if self.deputy_mayor.v is not None:
            self.deputy_mayor.v = str(self.deputy_mayor.v).strip()

    @override
    def export(self, ctx: TownSource) -> gt.Town:
        return gt.Town(**self._as_dict(ctx))

    @override
    def ref(self, ctx: TownSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(Town, name=self.name)
