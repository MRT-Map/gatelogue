from __future__ import annotations

from typing import ClassVar, Self, override

import gatelogue_types as gt

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.node.base import LocatedNode, NodeRef
from gatelogue_aggregator.types.source import Source


class SpawnWarpSource(BaseContext, Source):
    pass


class SpawnWarp(gt.SpawnWarp, LocatedNode[SpawnWarpSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (LocatedNode,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SpawnWarpSource,
        *,
        name: str,
        warp_type: gt.WarpType,
        world: gt.World | None = None,
        coordinates: tuple[float, float] | None = None,
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
    def export(self, ctx: SpawnWarpSource) -> gt.SpawnWarp:
        return gt.SpawnWarp(**self._as_dict(ctx))

    @override
    def ref(self, ctx: SpawnWarpSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(SpawnWarp, name=self.name)
