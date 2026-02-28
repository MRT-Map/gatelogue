from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.source import BusSource


def SOURCES() -> list[type[BusSource]]:  # noqa: N802
    from gatelogue_aggregator.sources.bus.ccc import CCC  # noqa: PLC0415
    from gatelogue_aggregator.sources.bus.intrabus import IntraBus  # noqa: PLC0415
    from gatelogue_aggregator.sources.bus.intrabus_warp import IntraBusWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.bus.omegabus import IntraBusOmegaBus  # noqa: PLC0415
    from gatelogue_aggregator.sources.bus.seabeast_buses import SeabeastBuses  # noqa: PLC0415

    return [CCC, IntraBus, IntraBusWarp, IntraBusOmegaBus, SeabeastBuses]
