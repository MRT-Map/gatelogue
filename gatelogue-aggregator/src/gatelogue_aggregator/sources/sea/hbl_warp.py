import contextlib
import itertools
import re
import uuid

import rich

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.logging import ERROR
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import SeaSource

# Adapted from https://docs.google.com/spreadsheets/d/1nIIettVbGwzm7DkmYqqPVoguw2U53R5un4nrC76w-Xg/edit#gid=1423194214
_DICT = {
    "ACH": "Achowalogen Takachsin",
    "ACR": "New Acreadium",
    "AIR": "Airchester",
    "ANT": "Anthro Island",
    "AQI": "Aquidneck Islands",
    "AUB": "Auburn",
    "AXB": "Alexandriasburg",
    "BAK": "Bakersville",
    "BAY": "Bay Point",
    "BBV": "Bobbyville",
    "BEA": "Beach City",
    "BIW": "Biwabik",
    "BLA": "Blackfriars",
    "BVW": "Beachview",
    "CEL": "Celina",
    "CHG": "Chugsdy Island",
    "CHW": "Chowder",
    "COV": "Covina",
    "CPC": "Cape Cambridge",
    "DAN": "Dand",
    "DEA": "Deadbush",
    "EDN": "Eden",
    "ELC": "Elecna Crescent",
    "ELE": "Elecna Bay",
    "ELF": "Ellerton Fosby",
    "EMS": "East Mesa",
    "ENB": "East New Brazil",
    "ENS": "Enspington",
    "ERZ": "Erzville",
    "FYX": "Fort Yaxier",
    "GAD": "Gorre & Daphetid",
    "GEN": "Geneva Bay",
    "GIL": "Gillmont",
    "GRW": "Greenwolf",
    "GRY": "Gray Cloud",
    "HAM": "Hamblin",
    "HEA": "Heampstead",
    "HUM": "Hummingbird Islands",
    "ILI": "Ilirea",
    "INS": "Insula Montes",
    "IOC": "Isle of Chez",
    "ITK": "Itokani",
    "JIM": "Jimbo",
    "KAN": "Kantō",
    "KAP": "Kappen",
    "KAZ": "Kazeshima",
    "KEN": "Kenthurst",
    "KLE": "Kleinsburg",
    "LAC": "Laclede",
    "LAP": "Lapis Bay",
    "LEG": "Lego City",
    "LEV": "Levittown",
    "LOS": "Los Angeles",
    "LPL": "Las Playas",
    "M10": "Mole Isle",
    "MAL": "Malosa",
    "MAR": "MRT Marina",
    "MAS": "Mason City",
    "MCK": "New Mackinaw",
    "MNI": "Monte Isola",
    "MOA": "Moramoa",
    "MOL": "Mole Island",
    "MOR": "Morihama",
    "MSL": "Marisol",
    "MTM": "Metamesa",
    "MUR": "Murrville",
    "MWN": "Miu Wan",
    "NBK": "New Bakersville City",
    "NSG": "New Singapore",
    "ONE": "Onemalu",
    "OPA": "Oparia",
    "OTT": "Ottia Islands",
    "PCH": "Peach Bay",
    "PIX": "Pixl",
    "PRA": "Praimina",
    "PSM": "Port Smith",
    "PSY": "Port Sybil",
    "REF": "Refuge",
    "RIS": "Risima",
    "RIZ": "Rizalburg",
    "RJN": "Richard's Junction",
    "RNB": "Rainer Bay",
    "ROK": "Roke",
    "ROS": "New Rosemont",
    "RRI": "Railroad Isle",
    "SAN": "Sansmore",
    "SCH": "Schillerton",
    "SCV": "Sunshine Cove",
    "SDP": "Shadowpoint",
    "SEA": "Seaview",
    "SEC": "Secunda",
    "SEH": "Seolho",
    "SEO": "Seoland",
    "SEU": "Seuland",
    "SHA": "Shahai",
    "SHN": "Shenghua",
    "SND": "Sand",
    "SOI": "Soiled Solitude",
    "SPL": "Spleef Island",
    "STA": "St. Anna",
    "STK": "Stockton",
    "STO": "Stoneedge",
    "SUN": "Sunshine Coast",
    "SVK": "Sansvikk",
    "SVZ": "San Vincenzo",
    "SWF": "Strawford",
    "TIT": "Titsensaki",
    "TTL": "TurtleLand",
    "TUL": "Tulipsburg",
    "TWE": "Tweebuffel",
    "VAN": "Vannahelm",
    "VDM": "Verdantium",
    "VEN": "Ventura Harbor",
    "VER": "Vermilion",
    "VIC": "Victoria",
    "VVL": "Victorville",
    "WAV": "Waverly",
    "WEN": "Wenyanga",
    "WEZ": "Weezerville",
    "WHI": "Whitechapel",
    "WHY": "Whiteley",
    "ZAQ": "Zaquar",
}


class HBLWarp(SeaSource):
    name = "MRT Warp API (Sea, Hummingbird Boat Lines)"
    warps: list[dict]

    def prepare(self, config: Config):
        self.warps = list(itertools.chain(
            warps(uuid.UUID("c04532bc-45d7-4d89-a13f-1d3bb4b48f2a"), config),
            warps(uuid.UUID("8a928931-aa14-4a1c-8a39-0a7630922001"), config),
        ))

    def build(self, config: Config):
        company = self.company(name="Hummingbird Boat Lines")

        names = list(_DICT.values())
        for warp in self.warps:
            if (result := re.match(r"HBL_(...)_(.*)", warp["name"])) is None:
                continue
            if (name := _DICT.get(result.group(1))) is None:
                rich.print(ERROR + f"Unknown warp {warp['name']}")
                continue
            if name not in ("Covnia", "Kenthurst") and name not in names:
                continue
            if name == "Covina":
                if result.group(2) in ("1", "10", "66"):
                    name += " (marina)"
                elif result.group(2) in ("55", "57", "58"):
                    name += " (canal)"
            elif name == "Kenthurst":
                if result.group(2) == "9":
                    name += " (west)"
                elif result.group(2) in ("22", "24", "51", "55"):
                    name += " (north)"

            self.stop(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            with contextlib.suppress(ValueError):
                names.remove(name)

        names.remove("Covina")
        names.remove("Kenthurst")
        if names:
            rich.print(ERROR + f"Not found: {', '.join(names)}")
