import re

import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource
from gatelogue_aggregator.utils import search_all


class BluRail(RailSource):
    name = "MRT Wiki (Rail, BluRail)"
    priority = 0

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="BluRail")

        for line_code in (
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "8",
            "9",
            "11",
            "12",
            "14",
            "16",
            "20",
            "23",
            "1X",
            "2X",
            "3X",
            "7X",
            "14X",
            "18X",
            "AA",
            "AB",
            "BS",
            "CS",
            "ES",
            "FC",
            "FY",
            "GC",
            "GS",
            "IS",
            "JC",
            "KS",
            "LC",
            "NF",
            "NI",
            "OP",
            "OS",
            "PC",
            "PS",
            "PX",
            "RC",
            "SF",
            "SN",
            "TS",
            "WC",
            "WS",
        ):
            wiki = get_wiki_text(f"{line_code} (BluRail line)", config)
            line_name = re.search(r"\| linelong = (.*)\n", wiki).group(1)
            line = self.rail_line(code=line_code, name=line_name, company=company, mode="warp")

            stations = []
            for result in search_all(re.compile(r"\|-\n\|(?!<s>)(?P<code>.*?)\n\|(?P<name>.*?)\n"), wiki):
                code = result.group("code").upper()
                if code == "BCH":
                    code += line_code
                elif code == "MCN" and line_code in ("11", "6"):
                    code += "11"
                elif code == "STE" and line_code == "1":
                    code += "1"
                codes = {
                    "ILI": {"ILI", "ITC"},
                    "ITC": {"ILI", "ITC"},
                    "SEA": {"SLC", "SEA"},
                    "SLC": {"SLC", "SEA"},
                    "IKA": {"UIK", "IKA"},
                    "UIK": {"UIK", "IKA"},
                    "EGN": {"EBN", "EGN"},
                    "EBN": {"EBN", "EGN"},
                    "SPN": {"FDR", "SPN"},
                    "FDR": {"FDR", "SPN"},
                }.get(code, {code})
                name = result.group("name").strip()
                if name == "":
                    continue
                station = self.rail_station(codes=codes, name=name, company=company)
                stations.append(station)

            if line_code == "2":
                RailLineBuilder(self, line).connect(*stations[:-3])
                RailLineBuilder(self, line).connect(*stations[-3:])
            elif line_code == "2X":
                RailLineBuilder(self, line).connect(*stations[:-2])
                RailLineBuilder(self, line).connect(*stations[-2:])
            elif line_code == "11":
                RailLineBuilder(self, line).connect(*stations[:-5])
                RailLineBuilder(self, line).connect(*stations[-5:])
            else:
                RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"BluRail Line {line_code} has {len(stations)} stations")
        self.save_to_cache(config, self.g)
