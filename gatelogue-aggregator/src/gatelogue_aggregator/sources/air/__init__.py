from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from gatelogue_aggregator.source import AirSource


def SOURCES() -> list[type[AirSource]]:  # noqa: N802
    from gatelogue_aggregator.sources.air.wiki_extractors.airline import AIRLINE_SOURCES

    return [
        #DynmapAirports,
        *AIRLINE_SOURCES,
        #MRTTransit,
        #*AIRPORT_SOURCES,
    ]
