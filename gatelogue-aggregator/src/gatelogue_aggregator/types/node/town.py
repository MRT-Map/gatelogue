from __future__ import annotations

import dataclasses
from typing import Literal, Self, override, ClassVar

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.node.base import LocatedNode, NodeRef
from gatelogue_aggregator.types.source import Source, Sourced


class TownSource(BaseContext, Source):
    pass


class Town(LocatedNode[TownSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (LocatedNode,)  # noqa: E731

    name: str
    """Name of the town"""
    rank: Sourced[Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]]
    """Rank of the town"""
    mayor: Sourced[str]
    """Mayor of the town"""
    deputy_mayor: Sourced[str | None]
    """Deputy Mayor of the town"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: TownSource,
        *,
        name: str,
        rank: Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"],
        mayor: str,
        deputy_mayor: str | None,
        world: Literal["New", "Old"] | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        self = super().new(
            ctx,
            world=world,
            coordinates=coordinates,
            name=name,
            rank=ctx.source(rank),
            mayor=ctx.source(mayor),
            deputy_mayor=ctx.source(deputy_mayor),
        )
        return self

    @override
    def str_ctx(self, ctx: TownSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: TownSource, other: Self) -> bool:
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
    def prepare_export(self, ctx: TownSource):
        super().prepare_export(ctx)

    @override
    def ref(self, ctx: TownSource) -> NodeRef[Self]:
        return NodeRef(Town, name=self.name)
