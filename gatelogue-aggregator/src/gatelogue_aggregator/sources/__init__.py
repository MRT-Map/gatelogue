from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.source import Source


def SOURCES() -> list[type[Source]]:  # noqa: N802
    from gatelogue_aggregator.sources.air import SOURCES as SOURCES_AIR  # noqa: PLC0415
    from gatelogue_aggregator.sources.bus import SOURCES as SOURCES_BUS  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail import SOURCES as SOURCES_RAIL  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea import SOURCES as SOURCES_SEA  # noqa: PLC0415
    from gatelogue_aggregator.sources.spawn_warp import SpawnWarps  # noqa: PLC0415
    from gatelogue_aggregator.sources.town import TownList  # noqa: PLC0415

    return [*SOURCES_AIR(), *SOURCES_BUS(), *SOURCES_SEA(), *SOURCES_RAIL(), SpawnWarps, TownList]
