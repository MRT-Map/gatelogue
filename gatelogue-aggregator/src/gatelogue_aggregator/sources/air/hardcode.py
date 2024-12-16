from __future__ import annotations

from typing import Literal

DIRECTIONAL_FLIGHT_AIRLINES: dict[str, Literal["even-odd", "odd-even"]] = {
    "MRT Airlines": "odd-even",
    "ArcticAir": "odd-even",
    "MarbleAir": "odd-even",
    "CampLines": "odd-even",
    "Rainer Airways": "odd-even",
    "AmberAir": "odd-even",
}

DUPLICATE_GATE_NUM: tuple[str, ...] = ("MAX", "SHI", "NWT", "NMW")

AIRLINE_ALIASES: dict[str, str] = {
    "Aero": "aero",
    "Air": "air",
    "Amber Airlines": "AmberAir",
    "Berryessa Airlines": "Infamous Airlines",
    "BluAir Hub Hopper": "BluAir",
    "Caelus Airlines/ikeda": "Caelus Airlines",
    "Caelus": "Caelus Airlines",
    "Cascadia": "Cascadia Airways",
    "CypressAir": "Cypress Air",
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
    "OLA": "Oceanic Langus Airways",
    "RedWave Airways": "RedWave",
    "rosa": "Rosa",
    "Sandstone Air": "ArcticAir",
    "Sandstone Airr": "ArcticAir",
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
    "DPH": "DBI",
    "COI": "COA",
    "TTL": "MWT",
    "LTN": "LNT",
}

GATE_ALIASES: dict[str, dict[str | tuple[str, str], str]] = {
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
}
