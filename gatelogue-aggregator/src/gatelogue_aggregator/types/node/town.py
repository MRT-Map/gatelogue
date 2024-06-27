from __future__ import annotations

import dataclasses
from typing import override, Container, Any, Self, Literal

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Source, Sourced
from gatelogue_aggregator.types.node.base import LocatedNode


class _TownContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class Town(LocatedNode[_TownContext]):
    acceptable_list_node_types = lambda: (LocatedNode,)  # noqa: E731

    @override
    def __init__(
        self,
        ctx: TownContext,
        source: type[TownContext] | None = None,
        *,
        name: str,
        **attrs,
    ):
        super().__init__(ctx, source, name=name, **attrs)

    @override
    def str_ctx(self, ctx: TownContext, filter_: Container[str] | None = None) -> str:
        return self.merged_attr(ctx, "name")

    @override
    @dataclasses.dataclass(unsafe_hash=True, kw_only=True)
    class Attrs(LocatedNode.Attrs):
        name: str
        rank: Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]
        mayor: str
        deputy_mayor: str | None

        @staticmethod
        @override
        def prepare_merge(source: Source, k: str, v: Any) -> Any:
            if k == "name":
                return v
            if k in ("rank", "mayor", "deputy_mayor"):
                return Sourced(v).source(source)
            return LocatedNode.Attrs.prepare_merge(source, k, v)

        @override
        def merge_into(self, source: Source, existing: dict[str, Any]):
            super().merge_into(source, existing)
            self.sourced_merge(source, existing, "rank")
            self.sourced_merge(source, existing, "mayor")
            self.sourced_merge(source, existing, "deputy_mayor")

    @override
    class Ser(LocatedNode.Ser, kw_only=True):
        name: str
        """Name of the town"""
        rank: Sourced.Ser[Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]]
        """Rank of the town"""
        mayor: Sourced.Ser[str]
        """Mayor of the town"""
        deputy_mayor: Sourced.Ser[str | None]
        """Deputy Mayor of the town"""

    def ser(self, ctx: TownContext) -> Town.Ser:
        return self.Ser(
            **self.merged_attrs(ctx),
            proximity=self.get_proximity_ser(ctx),
        )

    @override
    def equivalent(self, ctx: TownContext, other: Self) -> bool:
        return self.merged_attr(ctx, "name") == other.merged_attr(ctx, "name")

    @override
    def merge_key(self, ctx: TownContext) -> str:
        return self.merged_attr(ctx, "name")


class TownContext(_TownContext):
    @override
    class Ser(msgspec.Struct, kw_only=True):
        import uuid

        town: dict[uuid.UUID, Town.Ser]

    def ser(self, _=None) -> TownContext.Ser:
        return TownContext.Ser(
            town={a.id: a.ser(self) for a in self.g.nodes if isinstance(a, Town)},
        )

    def town(self, source: type[TownContext] | None = None, *, name: str, **attrs) -> Town:
        for n in self.g.nodes:
            if not isinstance(n, Town):
                continue
            if n.merged_attr(self, "name") == name:
                return n
        return Town(self, source, name=name, **attrs)


class TownSource(TownContext, Source):
    pass
