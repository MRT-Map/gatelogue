from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.source import SeaSource


def SOURCES() -> list[type[SeaSource]]:  # noqa: N802
    from gatelogue_aggregator.sources.sea.aqualinq import AquaLinQ  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.aqualinq_warp import AquaLinQWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.cfc import CFC  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.hbl import HBL  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.hbl_warp import HBLWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.intrasail import IntraSail  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.intrasail_warp import IntraSailWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.local.erzlink_ferry import ErzLinkFerry  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.local.windboat import Windboat  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.wzf import WZF  # noqa: PLC0415
    from gatelogue_aggregator.sources.sea.wzf_warp import WZFWarp  # noqa: PLC0415

    return [AquaLinQ, AquaLinQWarp, CFC, HBL, HBLWarp, IntraSail, IntraSailWarp, WZF, WZFWarp, ErzLinkFerry, Windboat]
