from __future__ import annotations

from typing import ClassVar, Literal, Self, override

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.node.base import LocatedNode, NodeRef, World
from gatelogue_aggregator.types.source import Source


class SpawnWarpSource(BaseContext, Source):
    pass


class SpawnWarp(LocatedNode[SpawnWarpSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (LocatedNode,)

    name: str
    """Name of the spawn warp"""
    warp_type: Literal["premier", "terminus", "portal", "misc"]
    """The type of warp"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SpawnWarpSource,
        *,
        name: str,
        warp_type: Literal["premier", "terminus", "portal", "misc"],
        world: World | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        return super().new(
            ctx,
            world=world,
            coordinates=coordinates,
            name=name,
            warp_type=warp_type,
        )

    @override
    def str_ctx(self, ctx: SpawnWarpSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: SpawnWarpSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: SpawnWarpSource, other: Self):
        super().merge_attrs(ctx, other)

    @override
    def merge_key(self, ctx: SpawnWarpSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.name = str(self.name).strip()
        # noinspection PyTypeChecker
        self.warp_type = str(self.warp_type).strip()

    @override
    def prepare_export(self, ctx: SpawnWarpSource):
        super().prepare_export(ctx)

    @override
    def ref(self, ctx: SpawnWarpSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(SpawnWarp, name=self.name)


Rank = Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]
