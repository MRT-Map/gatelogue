import json
import re

import rich

from gatelogue_aggregator.downloader import get_url
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

        line_list = json.loads(
            get_url(
                "https://wiki.minecartrapidtransit.net/api.php?action=query&list=categorymembers&cmtitle=Category%3ABluRail+lines&cmlimit=5000&format=json",
                config.cache_dir / "blurail_line_list",
                config.timeout,
            )
        )["query"]["categorymembers"]

        line_codes = [result["title"].removesuffix(" (BluRail line)") for result in line_list]

        for line_code in line_codes:
            wiki = get_wiki_text(f"{line_code} (BluRail line)", config)
            if "is a planned [[BluRail]] warp train line" in wiki:
                continue
            line_name = re.search(r"\| linelong = (.*)\n", wiki).group(1)

            line_colour = (
                "#c01c22"
                if line_code.endswith("X") and line_code[0].isdigit()
                else "#0a7ec3"
                if line_code[-1].isdigit()
                else "#0c4a9e"
            )

            line = RailLine.new(self, code=line_code, name=line_name, company=company, mode="warp", colour=line_colour)

            stations = []
            for result in search_all(re.compile(r"\|-\n\|(?!<s>)(?P<code>.*?)\n\|(?P<name>.*?)\n"), wiki):
                code = result.group("code").upper()
                if code == "BCH" and line_code in ("1", "18"):
                    code += "1"
                elif code == "MCN" and line_code in ("11", "6", "20"):
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
                RailLineBuilder(self, line).connect(*stations, between=(None, "Bay Point"))
                RailLineBuilder(self, line).connect(*stations, between=("Whitecliff Central", None))
            elif line_code == "2X":
                RailLineBuilder(self, line).connect(*stations, between=(None, "Pine Mountain Airfield"))
                RailLineBuilder(self, line).connect(*stations, between=("Segav Sal", None))
            else:
                RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"BluRail Line {line_code} has {len(stations)} stations")
        self.save_to_cache(config, self.g)
