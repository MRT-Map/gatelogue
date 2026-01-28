from __future__ import annotations

from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.bus.ccc import CCC
from gatelogue_aggregator.sources.bus.intrabus import IntraBus
from gatelogue_aggregator.sources.bus.intrabus_warp import IntraBusWarp
from gatelogue_aggregator.sources.bus.omegabus import IntraBusOmegaBus
from gatelogue_aggregator.sources.bus.seabeast_buses import SeabeastBuses

if TYPE_CHECKING:
    from gatelogue_aggregator.source import BusSource


def SOURCES() -> list[type[BusSource]]:  # noqa: N802

    return [
        CCC,
        IntraBus,
        IntraBusWarp,
        IntraBusOmegaBus,
        SeabeastBuses
    ]
