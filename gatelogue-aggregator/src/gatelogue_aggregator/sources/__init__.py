from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.source import Source


def SOURCES() -> list[type[Source]]:  # noqa: N802
    from gatelogue_aggregator.sources.air import SOURCES as SOURCES_AIR
    from gatelogue_aggregator.sources.bus import SOURCES as SOURCES_BUS
    from gatelogue_aggregator.sources.rail import SOURCES as SOURCES_RAIL
    from gatelogue_aggregator.sources.sea import SOURCES as SOURCES_SEA

    return [*SOURCES_AIR(), *SOURCES_BUS(), *SOURCES_SEA(), *SOURCES_RAIL(),]
