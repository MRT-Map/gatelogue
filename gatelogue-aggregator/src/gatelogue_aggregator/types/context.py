from __future__ import annotations

from typing import TYPE_CHECKING, Self, override

if TYPE_CHECKING:
    from collections.abc import Iterable

import rich
import rich.progress

from gatelogue_aggregator.types.air import AirContext
from gatelogue_aggregator.types.base import MergeableObject, Source, ToSerializable


class Context(AirContext, ToSerializable):
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

    @override
    class SerializableClass(AirContext.SerializableClass):
        pass

    @override
    def ser(self) -> SerializableClass:
        air = AirContext.ser(self)
        return self.SerializableClass(
            flight=air.flight,
            airport=air.airport,
            gate=air.gate,
            airline=air.airline,
        )
