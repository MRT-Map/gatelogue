from pathlib import Path

import pandas as pd
import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource


class NFLR(RailSource):
    name = "MRT Wiki (Rail, nFLR)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        cache = cache_dir / "nflr"
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="nFLR")

        for line_name, gid, w in (
            ("R1", 282537988, True),
            ("R1A", 214164635, False),
            ("R1C", 1902666542, False),
            ("R2", 115253128, True),
            ("R2A", 130508390, False),
            ("R2B", 1843528331, False),
            ("R2C", 221916670, False),
            ("R2D", 570220698, False),
            ("R3", 393671163, True),
            ("R4", 1996068267, True),
            ("R4A", 817280717, False),
            ("R5", 601855467, True),
            ("R5A", 507470974, False),
            ("R5B", 2076440356, False),
            ("R6", 1430738786, True),
            ("R7", 1926708521, True),
            ("R7A", 1818351657, False),
            ("R7Aα", 591894522, False),
            ("R7Aβ", 1399770737, False),
            ("R7B", 1247441432, False),
            ("R7C", 1332766054, False),
            ("R8", 1177310537, True),
            ("R8A", 1172467561, False),
            ("R9", 758399799, True),
            ("R10", 1201218447, True),
            ("R11", 320393003, True),
            ("R11A", 1797741201, False),
            ("R12", 1305691925, True),
            ("R12A", 902217973, False),
            ("R13", 131759497, True),
            ("R13A", 1377290085, False),
            ("R14", 1031060478, True),
            ("R15", 1924080573, True),
            ("R15A", 889243147, False),
            ("R16", 2087524175, True),
            ("R17", 1747108581, True),
            ("R18", 831892816, True),
            ("R19", 743645290, True),
            ("R20", 431509901, True),
            ("R21", 1760930420, True),
            ("R22", 334305123, True),
            ("R22A", 500206464, False),
            ("R23", 9575456, True),
            ("R24", 1618785684, True),
            ("AB", 1235587478, False),
            ("N1", 1882236259, False),
            ("N2", 497193857, False),
            ("N3", 978256843, False),
            ("N4", 1065941701, False),
        ):
            get_url(
                "https://docs.google.com/spreadsheets/d/1ohIRZrcLZByL5feqDqgA0QeC3uwAlBKOMKxWMRTSxRw/export?format=csv&gid="
                + str(gid),
                cache / line_name,
                timeout=timeout,
            )
            df = pd.read_csv(cache / line_name)

            d = list(zip(df["route"], df["code"], df["name"], strict=False))

            r_stations = []
            w_stations = []
            for route, code, name in d:
                code = {
                    "n104": {"n104", "n203", "n300"},
                    "n203": {"n104", "n203", "n300"},
                    "n300": {"n104", "n203", "n300"},
                    "hzc": {"hzc", "n213"},
                    "n213": {"hzc", "n213"},
                    "frg": {"frg", "n214"},
                    "n214": {"frg", "n214"},
                }.get(code, {code})
                station = None
                if "R" in route:
                    station = station or self.rail_station(codes=code, company=company, name=name)
                    r_stations.append(station)
                if "W" in route and w:
                    station = station or self.rail_station(codes=code, company=company, name=name)
                    w_stations.append(station)

            r_line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")

            if line_name == "R7A":
                RailLineBuilder(self, r_line).circle(
                    *r_stations, forward_label="clockwise", backward_label="anticlockwise"
                )
            elif line_name == "R5A":
                RailLineBuilder(self, r_line).connect(
                    *r_stations[:4], forward_label="southbound", backward_label="northbound"
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations[4:5], forward_label="southbound", backward_label="northbound CW"
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations[5:6], forward_label="northbound CCW", backward_label="southbound"
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations[6:], r_stations[1], forward_label="northbound", backward_label="southbound"
                )
            elif line_name == "R23":
                RailLineBuilder(self, r_line).connect(
                    *r_stations[: 9 - 3], *r_stations[12 - 3 :], forward_label="eastbound", backward_label="westbound"
                )
                RailLineBuilder(self, r_line).connect(
                    r_stations[8 - 3], r_stations[9 - 3], forward_label="to Sansvikk IKEA", backward_label="westbound"
                )
                RailLineBuilder(self, r_line).connect(
                    r_stations[12 - 3], r_stations[9 - 3], forward_label="to Sansvikk IKEA", backward_label="eastbound"
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations[9 - 3 : 12 - 3], forward_label="to Sansvikk IKEA", backward_label="to mainline"
                )
            else:
                RailLineBuilder(self, r_line).connect(*r_stations)

            rich.print(RESULT + f"nFLR Line {line_name} has {len(r_stations)} stations")

            if w:
                line_name = "W" + line_name[1:]
                w_line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
                RailLineBuilder(self, w_line).connect(*w_stations)
                rich.print(RESULT + f"nFLR Line {line_name} has {len(w_stations)} stations")
