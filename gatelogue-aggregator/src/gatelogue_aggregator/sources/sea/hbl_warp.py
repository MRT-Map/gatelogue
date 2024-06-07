import contextlib
import itertools
import re
import uuid
from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.logging import ERROR
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.sea import SeaContext, SeaSource

# Adapted from https://docs.google.com/spreadsheets/d/1nIIettVbGwzm7DkmYqqPVoguw2U53R5un4nrC76w-Xg/edit#gid=1423194214
_DICT = {
    "ACH": "Achowalogen Takachsin",
    "ACR": "New Acreadium",
    "AIR": "Airchester",
    "ANT": "Anthro Island",
    "AQI": "Aquidneck Islands",
    "AXB": "Alexandriasburg",
    "BAK": "Bakersville",
    "BAY": "Bay Point",
    "BEA": "Beach City",
    "BIW": "Biwabik",
    "BVW": "Beachview",
    "CEL": "Celina",
    "CHG": "Chugsdy Island",
    "COV": "Covina",
    "CPC": "Cape Cambridge",
    "DEA": "Deadbush",
    "EDN": "Eden",
    "ELC": "Elecna Crescent",
    "ELE": "Elecna Bay",
    "ELF": "Ellerton Fosby",
    "EMS": "East Mesa",
    "ENB": "East New Brazil",
    "ENS": "Enspington",
    "FYX": "Fort Yaxier",
    "GAD": "Gorre & Daphetid",
    "GEN": "Geneva Bay",
    "GIL": "Gillmont",
    "GRY": "Gray Cloud",
    "HEA": "Heapstead",
    "HUM": "Hummingbird Islands",
    "ILI": "Ilirea",
    "INS": "Insula Montes",
    "IOC": "Isle of Chez",
    "ITK": "Itokani",
    "JIM": "Jimbo",
    "KAN": "Kanto",
    "KAP": "Kappen",
    "KAZ": "Kazeshima",
    "KEN": "Kenthurst",
    "KLE": "Kleinsburg",
    "LAC": "Lacklede",
    "LAP": "Lapis Bay",
    "LEG": "Lego City",
    "LEV": "Levittown",
    "LOS": "Los Angeles",
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
    "NBK": "New Bakersville City",
    "NSG": "New Singapore",
    "ONE": "Onemalu",
    "OPA": "Oparia",
    "OTT": "Ottia Islands",
    "PIX": "Pixl",
    "PRA": "Praimina",
    "PSM": "Port Smith",
    "RIS": "Risima",
    "RIZ": "Rizalburg",
    "RJN": "Richard's Junction",
    "ROK": "Roke",
    "ROS": "New Rosemont",
    "RRI": "Railroad Isle",
    "SAN": "Sansmore",
    "SCH": "Schillerton",
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
    "STO": "Stoneedge",
    "SUN": "Sunshine Coast",
    "SVK": "Sansvikk",
    "SVZ": "San Vincenzo",
    "TIT": "Titsensaki",
    "TUL": "Tulipsburg",
    "TWE": "Tweebuffel",
    "VDM": "Verdantium",
    "VEN": "Ventura Harbor",
    "VER": "Vermilion",
    "VIC": "Victoria",
    "WAV": "Waverly",
    "WEN": "Wenyanga",
    "WEZ": "Weezerville",
    "WHI": "Whitechapel",
    "WHY": "Whiteley",
    "ZAQ": "Zaquar",
}


class HBLWarp(SeaSource):
    name = "MRT Warp API (Sea, Hummingbird Boat Lines)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        SeaContext.__init__(self)
        Source.__init__(self)

        company = self.sea_company(name="Hummingbird Boat Lines")

        names = list(_DICT.values())
        for warp in itertools.chain(
            warps(uuid.UUID("c04532bc-45d7-4d89-a13f-1d3bb4b48f2a"), cache_dir, timeout),
            warps(uuid.UUID("8a928931-aa14-4a1c-8a39-0a7630922001"), cache_dir, timeout),
        ):
            if (result := re.match(r"HBL_(...)_(.*)", warp["name"])) is None:
                continue
            if (name := _DICT.get(result.group(1))) is None:
                rich.print(ERROR + f"Unknown warp {warp['name']}")
                continue
            if name not in ("Covnia", "Kenthurst") and name not in names:
                continue
            if name == "Covina":
                if result.group(2) in ("1", "10"):
                    name += " (marina)"
                elif result.group(2) in ("55", "57", "58"):
                    name += " (canal)"
            elif name == "Kenthurst":
                if result.group(2) == "9":
                    name += " (west)"
                elif result.group(2) in ("22", "24", "51", "55"):
                    name += " (north)"

            self.sea_stop(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            with contextlib.suppress(ValueError):
                names.remove(name)

        names.remove("Covina")
        names.remove("Kenthurst")
        if names:
            rich.print(ERROR + f"Not found: {', '.join(names)}")
