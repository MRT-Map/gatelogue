from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import rich

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.source import Source


class NFLR(RailSource):
    name = "MRT Wiki (Rail, nFLR)"
    priority = 1

    def __init__(self, config: Config):
        cache = config.cache_dir / "nflr"
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="nFLR")

        lines = (
            ("R1", 282537988, True, "#c00"),
            ("R1A", 214164635, False, "#c00"),
            ("R1C", 1902666542, False, "#c00"),
            ("R2", 115253128, True, "#ffa500"),
            ("R2A", 130508390, False, "#ffa500"),
            ("R2B", 1843528331, False, "#ffa500"),
            ("R2C", 221916670, False, "#ffa500"),
            ("R2D", 570220698, False, "#ffa500"),
            ("R3", 393671163, True, "#fe0"),
            ("R4", 1996068267, True, "#987654"),
            ("R4A", 817280717, False, "#987654"),
            ("R5", 601855467, True, "#008000"),
            ("R5A", 507470974, False, "#008000"),
            ("R5B", 2076440356, False, "#008000"),
            ("R6", 1430738786, True, "#0c0"),
            ("R7", 1926708521, True, "#0cc"),
            ("R7A", 1818351657, False, "#0cc"),
            ("R7Aα", 591894522, False, "#0cc"),  # noqa: RUF001
            ("R7Aβ", 1399770737, False, "#0cc"),
            ("R7B", 1247441432, False, "#0cc"),
            ("R7C", 1332766054, False, "#0cc"),
            ("R8", 1177310537, True, "#008b8b"),
            ("R8A", 1172467561, False, "#008b8b"),
            ("R9", 758399799, True, "#00c"),
            ("R10", 1201218447, True, None),
            ("R11", 320393003, True, None),
            ("R11A", 1797741201, False, None),
            ("R12", 1305691925, True, None),
            ("R12A", 902217973, False, None),
            ("R13", 131759497, True, "#555"),
            ("R13A", 1377290085, False, "#555"),
            ("R14", 1031060478, True, "#aaa"),
            ("R15", 1924080573, True, "#000"),
            ("R15A", 889243147, False, "#000"),
            ("R16", 2087524175, True, "#eee"),
            ("R17", 1747108581, True, "#c2b280"),
            ("R18", 831892816, True, "#bb9955"),
            ("R19", 743645290, True, "#000080"),
            ("R20", 431509901, True, "#965f46"),
            ("R21", 1760930420, True, "#8b3d2e"),
            ("R22", 334305123, True, "#a3501e"),
            ("R22A", 500206464, False, "#a3501e"),
            ("R23", 9575456, True, "#bb8725"),
            ("R24", 1618785684, True, "#3d291b"),
            ("AB", 1235587478, False, None),
            ("N1", 1882236259, False, "#8c0"),
            ("N2", 497193857, False, "#5cf"),
            ("N3", 978256843, False, "#f5f"),
            ("N4", 1065941701, False, "#fc0"),
        )

        def retrieve_urls(line_name: str, gid: int, *_args):
            get_url(
                "https://docs.google.com/spreadsheets/d/1ohIRZrcLZByL5feqDqgA0QeC3uwAlBKOMKxWMRTSxRw/export?format=csv&gid="
                + str(gid),
                cache / line_name,
                timeout=config.timeout,
            )

        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            list(executor.map(lambda s: retrieve_urls(*s), lines))

        def get_stn(sts, name):
            st = next((st for st in sts if st.name == name), None)
            if st is None:
                raise ValueError(f"{name} not in {','.join(s.name for s in sts)}")
            return st
        
        for line_name, _, w, line_colour in lines:
            df = pd.read_csv(cache / line_name)

            d = list(zip(df["route"], df["code"], df["name"], strict=False))

            r_stations = []
            w_stations = []
            for route, code, name in d:
                code = {  # noqa: PLW2901
                    "n104": {"n104", "n203", "n300"},
                    "n203": {"n104", "n203", "n300"},
                    "n300": {"n104", "n203", "n300"},
                    "n105": {"n105", "n202"},
                    "n202": {"n105", "n202"},
                    "hzc": {"hzc", "n213"},
                    "n213": {"hzc", "n213"},
                    "frg": {"frg", "n214"},
                    "n214": {"frg", "n214"},
                }.get(code, {code})
                station = None
                if "R" in route:
                    station = station or RailStation.new(self, codes=code, company=company, name=name)
                    r_stations.append(station)
                if "W" in route and w:
                    station = station or RailStation.new(self, codes=code, company=company, name=name)
                    w_stations.append(station)

            r_line = RailLine.new(
                self, code=line_name, name=line_name, company=company, mode="warp", colour=line_colour
            )

            if line_name == "R7A":
                RailLineBuilder(self, r_line).circle(
                    *r_stations, forward_label="clockwise", backward_label="anticlockwise"
                )
            elif line_name == "R5A":
                RailLineBuilder(self, r_line).connect(
                    *r_stations, between=(None, "Deadbush Euphorial"), forward_label="southbound", backward_label="northbound"
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations, between=("Deadbush Euphorial", "Deadbush Quarryville"), forward_label="southbound", backward_label="northbound CW"
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations, between=("Deadbush Quarryville", "Deadbush Johnston-Euphorial Airport"), forward_label="northbound CCW", backward_label="southbound"
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations, get_stn(r_stations, "Deadbush Karaj Expo"), between=("Deadbush Johnston-Euphorial Airport", None), forward_label="northbound", backward_label="southbound"
                )
            elif line_name == "R23":
                RailLineBuilder(self, r_line).connect(
                    *r_stations, exclude=["Sansvikk Kamprad Airfield", "Sansvikk Karlstad", "Sansvikk IKEA"], forward_label="eastbound", backward_label="westbound"
                )
                RailLineBuilder(self, r_line).connect(
                    get_stn(r_stations, "Glacierton"), get_stn(r_stations, "Sansvikk Kamprad Airfield"), forward_label="to Sansvikk IKEA", backward_label="westbound"
                )
                RailLineBuilder(self, r_line).connect(
                    get_stn(r_stations, "Port Dupont"), get_stn(r_stations, "Sansvikk Kamprad Airfield"), forward_label="to Sansvikk IKEA", backward_label="eastbound"
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations, between=("Sansvikk Kamprad Airfield", "Sansvikk IKEA"), forward_label="to Sansvikk IKEA", backward_label="to mainline"
                )
            elif line_name == "R2":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Deadbush Valletta Desert Airport"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Paralia", None))
            elif line_name == "R4":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Birmingham"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Cape Cambridge John Glenn Transit Centre", None))
            elif line_name == "R5":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Xterium North"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Weston East", None))
            elif line_name == "R13":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "PCE Terminal 2"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Lilygrove Union", None))
            elif line_name == "R17":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Dewford City Lometa"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Fort Torbay", None))
            else:
                RailLineBuilder(self, r_line).connect(*r_stations)

            rich.print(RESULT + f"nFLR Line {line_name} has {len(r_stations)} stations")

            if w:
                line_name = "W" + line_name[1:]  # noqa: PLW2901
                w_line = RailLine.new(
                    self, code=line_name, name=line_name, company=company, mode="warp", colour=line_colour
                )

                if line_name == "W2":
                    RailLineBuilder(self, w_line).connect(*w_stations, between=(None, "DFM T1 / Borderville"))
                    RailLineBuilder(self, w_line).connect(*w_stations, between=("Southbank", None))
                elif line_name == "W5":
                    RailLineBuilder(self, w_line).connect(*w_stations, between=(None, "Xterium North"))
                    RailLineBuilder(self, w_line).connect(*w_stations, between=("Weston East", None))
                else:
                    RailLineBuilder(self, w_line).connect(*w_stations)

                rich.print(RESULT + f"nFLR Line {line_name} has {len(w_stations)} stations")
        self.save_to_cache(config, self.g)
