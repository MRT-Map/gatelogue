from gatelogue_aggregator.sources.air.dynmap_airports import DynmapAirports
from gatelogue_aggregator.sources.air.mrt_transit import MRTTransit
from gatelogue_aggregator.sources.air.wiki_airline import WikiAirline
from gatelogue_aggregator.sources.air.wiki_airport import WikiAirport
from gatelogue_aggregator.sources.bus.intrabus import IntraBus
from gatelogue_aggregator.sources.bus.intrabus_warp import IntraBusWarp
from gatelogue_aggregator.sources.bus.omegabus import IntraBusOmegaBus
from gatelogue_aggregator.sources.rail.blurail import BluRail
from gatelogue_aggregator.sources.rail.blurail_warp import BluRailWarp
from gatelogue_aggregator.sources.rail.dynmap_mrt import DynmapMRT
from gatelogue_aggregator.sources.rail.fredrail import FredRail
from gatelogue_aggregator.sources.rail.fredrail_warp import FredRailWarp
from gatelogue_aggregator.sources.rail.intrarail import IntraRail
from gatelogue_aggregator.sources.rail.intrarail_warp import IntraRailWarp
from gatelogue_aggregator.sources.rail.marblerail import MarbleRail
from gatelogue_aggregator.sources.rail.marblerail_warp import MarbleRailWarp
from gatelogue_aggregator.sources.rail.nflr import NFLR
from gatelogue_aggregator.sources.rail.nflr_warp import NFLRWarp
from gatelogue_aggregator.sources.rail.nsc import NSC
from gatelogue_aggregator.sources.rail.nsc_warp import NSCWarp
from gatelogue_aggregator.sources.rail.railinq import RaiLinQ
from gatelogue_aggregator.sources.rail.railinq_warp import RaiLinQWarp
from gatelogue_aggregator.sources.rail.railnorth import RailNorth
from gatelogue_aggregator.sources.rail.railnorth_warp import RailNorthWarp
from gatelogue_aggregator.sources.rail.redtrain import RedTrain
from gatelogue_aggregator.sources.rail.redtrain_warp import RedTrainWarp
from gatelogue_aggregator.sources.rail.wiki_mrt import WikiMRT
from gatelogue_aggregator.sources.rail.wzr import WZR
from gatelogue_aggregator.sources.rail.wzr_warp import WZRWarp
from gatelogue_aggregator.sources.sea.aqualinq import AquaLinQ
from gatelogue_aggregator.sources.sea.aqualinq_warp import AquaLinQWarp
from gatelogue_aggregator.sources.sea.hbl import HBL
from gatelogue_aggregator.sources.sea.hbl_warp import HBLWarp
from gatelogue_aggregator.sources.sea.intrasail import IntraSail
from gatelogue_aggregator.sources.sea.intrasail_warp import IntraSailWarp
from gatelogue_aggregator.sources.sea.wzf import WZF
from gatelogue_aggregator.sources.sea.wzf_warp import WZFWarp
from gatelogue_aggregator.sources.town import TownList

SOURCES = [
    MRTTransit,
    DynmapAirports,
    WikiAirline,
    WikiAirport,
    BluRail,
    BluRailWarp,
    IntraRail,
    IntraRailWarp,
    RaiLinQ,
    RaiLinQWarp,
    WZR,
    WZRWarp,
    WikiMRT,
    DynmapMRT,
    AquaLinQ,
    AquaLinQWarp,
    HBL,
    HBLWarp,
    IntraSail,
    IntraSailWarp,
    WZF,
    WZFWarp,
    IntraBus,
    IntraBusWarp,
    IntraBusOmegaBus,
    TownList,
    NFLR,
    NFLRWarp,
    MarbleRail,
    MarbleRailWarp,
    NSC,
    NSCWarp,
    FredRail,
    FredRailWarp,
    RedTrain,
    RedTrainWarp,
    RailNorth,
    RailNorthWarp,
]
