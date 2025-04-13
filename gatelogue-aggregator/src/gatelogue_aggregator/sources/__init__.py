from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from gatelogue_aggregator.types.source import Source


def SOURCES() -> list[type[Source]]:  # noqa: N802
    from gatelogue_aggregator.sources.air.dynmap_airports import DynmapAirports
    from gatelogue_aggregator.sources.air.mrt_transit import MRTTransit
    from gatelogue_aggregator.sources.air.wiki_airline import WikiAirline
    from gatelogue_aggregator.sources.air.wiki_airport import WikiAirport
    from gatelogue_aggregator.sources.bus.ccc import CCC
    from gatelogue_aggregator.sources.bus.intrabus import IntraBus
    from gatelogue_aggregator.sources.bus.intrabus_warp import IntraBusWarp
    from gatelogue_aggregator.sources.bus.omegabus import IntraBusOmegaBus
    from gatelogue_aggregator.sources.bus.seabeast_buses import SeabeastBuses
    from gatelogue_aggregator.sources.rail.blurail import BluRail
    from gatelogue_aggregator.sources.rail.blurail_warp import BluRailWarp
    from gatelogue_aggregator.sources.rail.dynmap_mrt import DynmapMRT
    from gatelogue_aggregator.sources.rail.fredrail import FredRail
    from gatelogue_aggregator.sources.rail.intrarail import IntraRail
    from gatelogue_aggregator.sources.rail.intrarail_warp import IntraRailWarp
    from gatelogue_aggregator.sources.rail.local.flr_kaze import FLRKaze
    from gatelogue_aggregator.sources.rail.local.flr_sheng import FLRSheng
    from gatelogue_aggregator.sources.rail.marblerail import MarbleRail
    from gatelogue_aggregator.sources.rail.marblerail_warp import MarbleRailWarp
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
    from gatelogue_aggregator.sources.sea.aqualinq import AquaLinQ
    from gatelogue_aggregator.sources.sea.aqualinq_warp import AquaLinQWarp
    from gatelogue_aggregator.sources.sea.cfc import CFC
    from gatelogue_aggregator.sources.sea.hbl import HBL
    from gatelogue_aggregator.sources.sea.hbl_warp import HBLWarp
    from gatelogue_aggregator.sources.sea.intrasail import IntraSail
    from gatelogue_aggregator.sources.sea.intrasail_warp import IntraSailWarp
    from gatelogue_aggregator.sources.sea.wzf import WZF
    from gatelogue_aggregator.sources.sea.wzf_warp import WZFWarp
    from gatelogue_aggregator.sources.spawn_warp import SpawnWarps
    from gatelogue_aggregator.sources.town import TownList

    return [
        AquaLinQ,
        AquaLinQWarp,
        BluRail,
        BluRailWarp,
        CCC,
        CFC,
        DynmapAirports,
        DynmapMRT,
        FLRKaze,
        FLRSheng,
        FredRail,
        HBL,
        HBLWarp,
        IntraBus,
        IntraBusOmegaBus,
        IntraBusWarp,
        IntraRail,
        IntraRailWarp,
        IntraSail,
        IntraSailWarp,
        MarbleRail,
        MarbleRailWarp,
        MRTTransit,
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
        SeabeastBuses,
        SeabeastRail,
        SEAT,
        SEATWarp,
        SpawnWarps,
        TownList,
        WikiAirline,
        WikiAirport,
        WikiMRT,
        WZF,
        WZFWarp,
        WZR,
        WZRWarp,
    ]
