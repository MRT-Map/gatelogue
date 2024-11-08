from __future__ import annotations

import dataclasses
from typing import Literal, Self, override

from gatelogue_aggregator.types.base import BaseContext, Source, Sourced
from gatelogue_aggregator.types.node.base import LocatedNode, NodeRef


class _TownContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Town(LocatedNode[_TownContext]):
    acceptable_list_node_types = lambda: (LocatedNode,)  # noqa: E731

    name: str
    """Name of the town"""
    rank: Sourced[Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]]
    """Rank of the town"""
    mayor: Sourced[str]
    """Mayor of the town"""
    deputy_mayor: Sourced[str | None]
    """Deputy Mayor of the town"""

    @override
    def __init__(
        self,
        ctx: TownContext,
        *,
        name: str,
        rank: Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"],
        mayor: str,
        deputy_mayor: str | None,
        world: Literal["New", "Old"] | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        super().__init__(ctx, world=world, coordinates=coordinates)
        self.name = name
        self.rank = ctx.source(rank)
        self.mayor = ctx.source(mayor)
        self.deputy_mayor = ctx.source(deputy_mayor)

    @override
    def str_ctx(self, ctx: TownContext) -> str:
        return self.name

    @override
    def equivalent(self, ctx: TownContext, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: TownContext, other: Self):
        super().merge_attrs(ctx, other)
        self._merge_sourced(ctx, other, "rank")
        self._merge_sourced(ctx, other, "mayor")
        self._merge_sourced(ctx, other, "deputy_mayor")

    @override
    def merge_key(self, ctx: TownContext) -> str:
        return self.name

    @override
    def prepare_export(self, ctx: TownContext):
        super().prepare_export(ctx)

    @override
    def ref(self, ctx: TownContext) -> NodeRef[Self]:
        return NodeRef(Town, name=self.name)


class TownContext(_TownContext):
    pass


type TownSource = TownContext
