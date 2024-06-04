from typing import Literal

DIRECTIONAL_FLIGHT_AIRLINES: dict[str, Literal["even-odd", "odd-even"]] = {
    "MRT Airlines": "odd-even",
    "ArcticAir": "odd-even",
    "MarbleAir": "odd-even",
}

DUPLICATE_GATE_NUM: tuple[str, ...] = ("MAX", "SHI", "NWT")

AIRLINE_ALIASES: dict[str, str] = {
    "Aero": "aero",
    "Air": "air",
    "Amber Airlines": "AmberAir",
    "Berryessa Airlines": "Infamous Airlines",
    "BluAir Hub Hopper": "BluAir",
    "Caelus Airlines/ikeda": "Caelus Airlines",
    "Caelus": "Caelus Airlines",
    "Cascadia": "Cascadia Airways",
    "FliHigh": "FliHigh Airlines",
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
    "MRTHS Air": "Astrella",
    "myles": "mylesHeli",
    "mylesAir": "mylesHeli",
    "MylesHeli": "mylesHeli",
    "OLA": "Oceanic Langus Airways",
    "South Weast Charter": "South Weast Airlines",
    "SunAir": "FlyBahia",
    "ViaRapid": "ViaFly",
    "Waypoint": "IntraAir",
    "Waypoint Hopper": "IntraAir",
}

AIRPORT_ALIASES: dict[str, str] = {"DTS": "DCA", "RBE": "RBD", "IKLA": "KLA"}
