from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gatelogue_aggregator.source import RailSource


def SOURCES() -> list[type[RailSource]]:  # noqa: N802
    from gatelogue_aggregator.sources.rail.blurail import BluRail
    from gatelogue_aggregator.sources.rail.blurail_warp import BluRailWarp
    from gatelogue_aggregator.sources.rail.breezerail import BreezeRail
    from gatelogue_aggregator.sources.rail.breezerail_warp import BreezeRailWarp
    from gatelogue_aggregator.sources.rail.cvc_express import CVCExpress
    from gatelogue_aggregator.sources.rail.cvc_express_coord import CVCExpressCoord
    from gatelogue_aggregator.sources.rail.dynmap_mrt import DynmapMRT
    from gatelogue_aggregator.sources.rail.erzlink_intercity import ErzLinkIntercity
    from gatelogue_aggregator.sources.rail.fredrail import FredRail
    from gatelogue_aggregator.sources.rail.intrarail import IntraRail
    from gatelogue_aggregator.sources.rail.intrarail_warp import IntraRailWarp
    from gatelogue_aggregator.sources.rail.lava_rail import LavaRail
    from gatelogue_aggregator.sources.rail.local.erzlink_metro import ErzLinkMetro
    from gatelogue_aggregator.sources.rail.local.erzlink_trams import ErzLinkTrams
    from gatelogue_aggregator.sources.rail.local.flr_foresne import FLRForesne
    from gatelogue_aggregator.sources.rail.local.flr_kaze import FLRKaze
    from gatelogue_aggregator.sources.rail.local.flr_sheng import FLRSheng
    from gatelogue_aggregator.sources.rail.local.metro_de_ene import MetroDeEne
    from gatelogue_aggregator.sources.rail.local.np_subway import NPSubway
    from gatelogue_aggregator.sources.rail.local.refuge_streetcar import RefugeStreetcar
    from gatelogue_aggregator.sources.rail.marblerail import MarbleRail
    from gatelogue_aggregator.sources.rail.marblerail_coord import MarbleRailCoord
    from gatelogue_aggregator.sources.rail.nflr import NFLR
    from gatelogue_aggregator.sources.rail.nflr_warp import NFLRWarp
    from gatelogue_aggregator.sources.rail.nrn import NRN
    from gatelogue_aggregator.sources.rail.nsc import NSC
    from gatelogue_aggregator.sources.rail.nsc_warp import NSCWarp
    from gatelogue_aggregator.sources.rail.pacifica import Pacifica
    from gatelogue_aggregator.sources.rail.pacifica_coord import PacificaCoord
    from gatelogue_aggregator.sources.rail.railinq import RaiLinQ
    from gatelogue_aggregator.sources.rail.railinq_warp import RaiLinQWarp
    from gatelogue_aggregator.sources.rail.railnorth import RailNorth
    from gatelogue_aggregator.sources.rail.railnorth_warp import RailNorthWarp
    from gatelogue_aggregator.sources.rail.redtrain import RedTrain
    from gatelogue_aggregator.sources.rail.redtrain_warp import RedTrainWarp
    from gatelogue_aggregator.sources.rail.seabeast_rail import SeabeastRail
    from gatelogue_aggregator.sources.rail.seat import SEAT
    from gatelogue_aggregator.sources.rail.seat_warp import SEATWarp
    from gatelogue_aggregator.sources.rail.wiki_mrt import WikiMRT
    from gatelogue_aggregator.sources.rail.wzr import WZR
    from gatelogue_aggregator.sources.rail.wzr_warp import WZRWarp

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
