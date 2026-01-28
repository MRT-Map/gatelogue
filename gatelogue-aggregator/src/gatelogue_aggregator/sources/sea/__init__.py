from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.source import SeaSource


def SOURCES() -> list[type[SeaSource]]:  # noqa: N802
    from gatelogue_aggregator.sources.sea.aqualinq import AquaLinQ
    from gatelogue_aggregator.sources.sea.aqualinq_warp import AquaLinQWarp
    from gatelogue_aggregator.sources.sea.cfc import CFC
    from gatelogue_aggregator.sources.sea.hbl import HBL
    from gatelogue_aggregator.sources.sea.hbl_warp import HBLWarp
    from gatelogue_aggregator.sources.sea.intrasail import IntraSail
    from gatelogue_aggregator.sources.sea.intrasail_warp import IntraSailWarp
    from gatelogue_aggregator.sources.sea.local.erzlink_ferry import ErzLinkFerry
    from gatelogue_aggregator.sources.sea.local.windboat import Windboat
    from gatelogue_aggregator.sources.sea.wzf import WZF
    from gatelogue_aggregator.sources.sea.wzf_warp import WZFWarp

    return [
        AquaLinQ,
        AquaLinQWarp,
        CFC,
        HBL,
        HBLWarp,
        IntraSail,
        IntraSailWarp,
        WZF,
        WZFWarp,

        ErzLinkFerry,
        Windboat
    ]
