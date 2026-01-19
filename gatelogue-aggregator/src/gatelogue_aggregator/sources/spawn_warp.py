from typing import Literal

from gatelogue_aggregator.downloader import all_warps
from gatelogue_aggregator.logging import INFO3, track
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.spawn_warp import SpawnWarp, SpawnWarpSource


class SpawnWarps(SpawnWarpSource):
    name = "Gatelogue"
    priority = 0

    def build(self, config: Config):
        search_dict: dict[Literal["premier", "terminus", "traincarts", "misc"], set] = {
            "premier": {
                "Achowalogen",
                "Airchester",
                "Arisa",
                "Auburn",
                "Caravaca",
                ("ChanBay", "Chan Bay"),
                "Deadbush",
                "ElecnaBay",
                "Espil",
                "Evella",
                ("FirewoodCity", "Firewood City"),
                "Itokani",
                "Kenthurst",
                "Kessler",
                ("KolpinoCity", "Kolpino City"),
                "Laclede",
                "Lanark",
                "Larkspur",
                ("MiuWan", "Miu Wan"),
                "Mountbatten",
                ("NewChandigarh", "New Chandigarh"),
                "Nuuk",
                "Oparia",
                "Porton",
                "Quiris",
                "Redwood",
                "Segville",
                ("SunshineCoast", "Sunshine Coast"),
                "Utopia",
                "Venceslo",
                "Whitechapel",
            },
            "terminus": {
                "A1",
                "A78",
                "B0",
                "BS22",
                "C1",
                "C33",
                "C61",
                "C89",
                "D1",
                "D60",
                "EN52",
                "ES56",
                "F1",
                "F58",
                "Ga1",
                "G17",
                "H1",
                "H51",
                "I1",
                "I61",
                "JN19",
                "JS63",
                "KN22",
                "K0",
                "LW49",
                "LE22",
                "M1",
                "M90",
                "NW41",
                "NE30",
                "OW59",
                "O0",
                "P1",
                "P73",
                "RW7",
                "RE21",
                "SW49",
                "SE42",
                "T1",
                "T77",
                "U1",
                "U29",
                "U54",
                "U89",
                "U114",
                "U140",
                "U169",
                "U196",
                "V1",
                "V62",
                "WN60",
                "WS35",
                "XW57",
                "XE52",
                "YW11",
                "Y0",
                "ZN59",
                "ZS55",
            },
            "traincarts": {
                ("tc_aichalappa", "ANF Skytrain for Hotel Contest"),
                ("tc_ellerton", "Ellerton Fosby Tram"),
                ("tc_erzville_hc", "Erzville Hoverliner (boat)"),
                ("tc_glacierton", "Glacierton Metro"),
                ("tc_hendon", "Hendon for London 1938 Stock"),
                ("tc_intrabahn", "IntraBahn (non-attachment)"),
                ("tc_nobopolis", "Nobody's Rail Network"),
                ("tc_rainer_bay", "Rainer Bay Metro"),
                ("tc_refuge", "Refuge Streetcar"),
                ("tc_serena", "Serena Metro (ticket required)"),
                ("tc_treebark", "Treebark Gondola"),
            },
            "misc": {
                ("CCHP", "Central City Heliport"),
                ("CCTerminal", "Central City Warp Rail Terminal"),
                ("MRTLand", "MRT Land"),
                ("Marina", "MRT Marina"),
            },
        }

        for warp in track(all_warps(config), INFO3, description="Searching all warps for spawn warps", total=35000):
            for ty, search_list in search_dict.items():
                for search_warp in search_list:
                    if isinstance(search_warp, tuple):
                        search_warp, name = search_warp  # noqa: PLW2901
                    else:
                        name = search_warp

                    if search_warp != warp["name"]:
                        continue

                    SpawnWarp.new(
                        self,
                        name=name,
                        warp_type=ty,
                        world="New" if warp["worldUUID"] == "253ced62-9637-4f7b-a32d-4e3e8e767bd1" else "Old",
                        coordinates=(warp["x"], warp["z"]),
                    )

        SpawnWarp.new(self, name="Old World", warp_type="portal", world="Old", coordinates=(0, 0))
        SpawnWarp.new(self, name="Space World", warp_type="portal", world="Space", coordinates=(0, 0))
