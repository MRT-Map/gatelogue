from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from collections.abc import Iterable

import rich
import rich.progress

from gatelogue_aggregator.types.air import AirContext
from gatelogue_aggregator.types.base import MergeableObject, Source


class Context(AirContext):
    @classmethod
    def from_sources(cls, sources: Iterable[Source]) -> Self:
        self = cls()
        for source in rich.progress.track(sources, f"[yellow]Merging sources: {', '.join(s.name for s in sources)}"):
            if isinstance(source, AirContext):
                MergeableObject.merge_lists(self.flight, source.flight)
                MergeableObject.merge_lists(self.airport, source.airport)
                MergeableObject.merge_lists(self.gate, source.gate)
                MergeableObject.merge_lists(self.airline, source.airline)
        return self

    def update(self):
        AirContext.update(self)

    def dict(self) -> dict[str, dict[str, Any]]:
        return AirContext.dict(self)
