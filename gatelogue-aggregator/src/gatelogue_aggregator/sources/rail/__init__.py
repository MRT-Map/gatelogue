from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.source import RailSource


def SOURCES() -> list[type[RailSource]]:  # noqa: N802
    from gatelogue_aggregator.sources.rail.local.erzlink_metro import ErzLinkMetro
    from gatelogue_aggregator.sources.rail.local.erzlink_trams import ErzLinkTrams
    from gatelogue_aggregator.sources.rail.local.flr_foresne import FLRForesne
    from gatelogue_aggregator.sources.rail.local.flr_kaze import FLRKaze
    from gatelogue_aggregator.sources.rail.local.flr_sheng import FLRSheng
    from gatelogue_aggregator.sources.rail.local.metro_de_ene import MetroDeEne
    from gatelogue_aggregator.sources.rail.local.np_subway import NPSubway
    from gatelogue_aggregator.sources.rail.local.refuge_streetcar import RefugeStreetcar

    return [ErzLinkMetro, ErzLinkTrams, FLRForesne, FLRKaze, FLRSheng, MetroDeEne, NPSubway, RefugeStreetcar]
