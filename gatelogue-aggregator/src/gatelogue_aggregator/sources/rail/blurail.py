import re

import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.source import Source
from gatelogue_aggregator.utils import search_all


class BluRail(RailSource):
    name = "MRT Wiki (Rail, BluRail)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="BluRail")

        line_list = get_wiki_text("List of BluRail lines", config)
        line_codes = [
            result.group("code")
            for result in search_all(
                re.compile(r"{{BR\|(?P<code>[^}]+)}}\n\|.*\n\|.*\n\|.*\n\|(?P<adv>.*)\n\|"), line_list
            )
            if "planned service" not in result.group("adv").lower()
        ]

        for line_code in line_codes:
            wiki = get_wiki_text(f"{line_code} (BluRail line)", config)
            line_name = re.search(r"\| linelong = (.*)\n", wiki).group(1)
            line = RailLine.new(self, code=line_code, name=line_name, company=company, mode="warp")

            stations = []
            for result in search_all(re.compile(r"\|-\n\|(?!<s>)(?P<code>.*?)\n\|(?P<name>.*?)\n"), wiki):
                code = result.group("code").upper()
                if code == "BCH":
                    code += line_code
                elif code == "MCN" and line_code in ("11", "6"):
                    code += "11"
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
                    "WCA": {"WCA", "WAI"},
                    "WAI": {"WCA", "WAI"},
                }.get(code, {code})
                name = result.group("name").strip()
                if name == "":
                    continue
                station = RailStation.new(self, codes=codes, name=name, company=company)
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
