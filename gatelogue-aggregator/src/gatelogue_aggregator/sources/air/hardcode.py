from __future__ import annotations

from typing import Literal

type Direction = Literal["even-odd", "odd-even"]

DIRECTIONAL_FLIGHT_AIRLINES: dict[str, Direction | list[tuple[range | None, Direction]]] = {
    "MRT Airlines": [
        (range(1294, 1296), "even-odd"),
        (range(8392, 8394), "even-odd"),
        (range(2960, 2962), "even-odd"),
        (range(6646, 6648), "even-odd"),
        (range(4554, 4556), "even-odd"),
        (None, "odd-even"),
    ],
    "ArcticAir": [
        (range(1000), "odd-even"),
        (None, "even-odd"),
    ],
    "MarbleAir": "odd-even",
    "CampLines": "odd-even",
    "Rainer Airways": "odd-even",
    "AmberAir": "odd-even",
    "Astrella": "odd-even",
    "Caelus Airlines": [
        (range(100), "odd-even"),
        (None, "even-odd"),
    ],
    "CaelusLink": "even-odd",
}

DUPLICATE_GATE_NUM: tuple[str, ...] = ("MAX", "SHI", "NWT", "NMW")

AIRLINE_ALIASES: dict[str, str] = {
    "Aero": "aero",
    "Air": "air",
    "Amber Airlines": "AmberAir",
    "Infamous Airlines": "Berryessa Airlines",
    "BluAir Hub Hopper": "BluAir",
    "Caelus Airlines/ikeda": "Caelus Airlines",
    "Caelus": "Caelus Airlines",
    "Cascadia": "Cascadia Airways",
    "CypressAir": "Cypress Air",
    "DAS": "IntraAir",
    "Eastern Airways": "IntraAir",
    "FliHigh": "FliHigh Airlines",
    "FlyHigh": "FliHigh Airlines",
    "FlyArctic": "Cascadia Airways",
    "FlyLumeva": "Astrella",
    "FlyMighty": "Infamous Airlines",
    "FlySakura": "Michigana",
    "FlySubway": "Astrella",
    "HarbourAir/Pan Aqua": "HarbourAir",
    "Infamous Eagle": "Oceanic Langus Airways",
    "IntraAir Heli Lines": "IntraAir",
    "IntraAir Poseidon": "IntraAir",
    "Kaloro Air": "Astrella",
    "KaloroAir": "Astrella",
    "LARLAT Airways": "Lilyflower Airlines",
    "MRTHS Air": "Astrella",
    "MRTHS": "Astrella",
    "myles": "mylesHeli",
    "mylesAir": "mylesHeli",
    "MylesHeli": "mylesHeli",
    "Myles Heli": "mylesHeli",
    "Nexus Airlines": "Nexus",
    "NextTrain": "NextPlane",
    "OLA": "Oceanic Langus Airways",
    "RedWave Airways": "RedWave",
    "Raiko Airlines": "Tennoji Airways",
    "rosa": "Rosa",
    "Sandstone Air": "ArcticAir",
    "Sandstone Airr": "ArcticAir",
    "Sandy Air": "FlyCreeper",
    "South Weast Charter": "South Weast Airlines",
    "Spirit": "Spirit Airlines",
    "SunAir": "FlyBahia",
    "Utopiair": "UtopiAir",
    "ViaRapid": "ViaFly",
    "Waypoint": "IntraAir",
    "Waypoint Hopper": "IntraAir",
}

AIRPORT_ALIASES: dict[str, str] = {
    "DTS": "DCA",
    "RBE": "RBD",
    "IKLA": "KLA",
    "ITO": "IAS",
    "COI": "COA",
    "TTL": "MWT",
    "LTN": "LNT",
    "KAZ": "KAO",
    "CBH": "CHH",
    "FQR": "FQA",
    "VEG": "VCA",
    "LMN": "LLM",
}

GATE_ALIASES: dict[str, dict[str | tuple[str, str], str | None]] = {
    "PCE": {
        "4": "C2",
        "5": "C3",
        "12": "C7",
    },
    "SHI": {
        "2-4": "T2-4",
    },
    "MAX": {
        ("Lilyflower Airlines", "A3"): "T1A3",
        ("Astrella", "B1"): "T2B1",
        "C7": "T1C7",
        "D4": "T1C22",
        "D14": "T1D4",
    },
    "NMW": {"T2G2": "T2-2"},
    "NWT": {"T2G2": "T2-2", "T2G5": "T2-5"},
    "DBI": {
        "1": "A1",
        "3": None,
        "4": "A4",
        "14": "A14",
        "21": "A21",
        "22": "A22",
        "28": "A28",
        "30": "A30",
    },
    "GSM": {"3": "A3", "7": "A7"},
    "ABG": {"3": "I3"},
}
