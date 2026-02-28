from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.source import RailSource


def SOURCES() -> list[type[RailSource]]:  # noqa: N802
    from gatelogue_aggregator.sources.rail.blurail import BluRail  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.blurail_warp import BluRailWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.breezerail import BreezeRail  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.breezerail_warp import BreezeRailWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.cvc_express import CVCExpress  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.cvc_express_coord import CVCExpressCoord  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.dynmap_mrt import DynmapMRT  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.erzlink_intercity import ErzLinkIntercity  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.fredrail import FredRail  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.intrarail import IntraRail  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.intrarail_warp import IntraRailWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.lava_rail import LavaRail  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.local.erzlink_metro import ErzLinkMetro  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.local.erzlink_trams import ErzLinkTrams  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.local.flr_foresne import FLRForesne  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.local.flr_kaze import FLRKaze  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.local.flr_sheng import FLRSheng  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.local.metro_de_ene import MetroDeEne  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.local.np_subway import NPSubway  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.local.refuge_streetcar import RefugeStreetcar  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.marblerail import MarbleRail  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.marblerail_coord import MarbleRailCoord  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.nflr import NFLR  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.nflr_warp import NFLRWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.nrn import NRN  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.nsc import NSC  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.nsc_warp import NSCWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.pacifica import Pacifica  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.pacifica_coord import PacificaCoord  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.railinq import RaiLinQ  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.railinq_warp import RaiLinQWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.railnorth import RailNorth  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.railnorth_warp import RailNorthWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.redtrain import RedTrain  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.redtrain_warp import RedTrainWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.seabeast_rail import SeabeastRail  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.seat import SEAT  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.seat_warp import SEATWarp  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.wiki_mrt import WikiMRT  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.wzr import WZR  # noqa: PLC0415
    from gatelogue_aggregator.sources.rail.wzr_warp import WZRWarp  # noqa: PLC0415

    return [
        ErzLinkMetro,
        ErzLinkTrams,
        FLRForesne,
        FLRKaze,
        FLRSheng,
        MetroDeEne,
        NPSubway,
        RefugeStreetcar,
        BluRail,
        BluRailWarp,
        BreezeRail,
        BreezeRailWarp,
        CVCExpress,
        CVCExpressCoord,
        DynmapMRT,
        ErzLinkIntercity,
        FredRail,
        IntraRail,
        IntraRailWarp,
        LavaRail,
        MarbleRail,
        MarbleRailCoord,
        NFLR,
        NFLRWarp,
        NRN,
        NSC,
        NSCWarp,
        Pacifica,
        PacificaCoord,
        RaiLinQ,
        RaiLinQWarp,
        RailNorth,
        RailNorthWarp,
        RedTrain,
        RedTrainWarp,
        SeabeastRail,
        SEAT,
        SEATWarp,
        WikiMRT,
        WZR,
        WZRWarp,
    ]
