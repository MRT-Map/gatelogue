import re

import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource
from gatelogue_aggregator.types.source import Source
from gatelogue_aggregator.utils import search_all


class WikiMRT(RailSource):
    name = "MRT Wiki (Rail, MRT)"
    priority = 0

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="MRT")

        for line_code, line_name in (
            ("A", "MRT Arctic Line"),
            ("C", "MRT Circle Line"),
            ("D", "MRT Desert Line"),
            ("E", "MRT Eastern Line"),
            ("F", "MRT Forest Line"),
            ("H", "MRT Savannah Line"),
            ("I", "MRT Island Line"),
            ("J", "MRT Jungle Line"),
            ("L", "MRT Lakeshore Line"),
            ("M", "MRT Mesa Line"),
            ("N", "MRT Northern Line"),
            ("O", "MRT Oasis Line"),
            ("P", "MRT Plains Line"),
            ("R", "MRT Rose Line"),
            ("S", "MRT Southern Line"),
            ("T", "MRT Taiga Line"),
            ("U", "MRT Union Line"),
            ("V", "MRT Valley Line"),
            ("W", "MRT Western Line"),
            ("X", "MRT Expo Line"),
            ("XM", "MRT Marina Shuttle"),
            ("Z", "MRT Zephyr Line"),
            ("Old-R", "MRT Red Line"),
            ("Old-B", "MRT Blue Line"),
            ("Old-Y", "MRT Yellow Line"),
            ("Old-G", "MRT Green Line"),
            ("Old-O", "MRT Orange Line"),
        ):
            text = get_wiki_text(line_name, config)
            line = self.rail_line(code=line_code, company=company, name=line_name)

            stations = []
            for match in search_all(
                re.compile(r"{{station\|open\|[^|]*?\|(?P<code>[^|]*?)\|(?P<transfers>.*?)}}\s*\n"), text
            ):
                codes = {match.group("code")}
                for match2 in search_all(
                    re.compile(r"{{st/n\|[^}]*\|([^}]*)}}|{{s\|([^}]*)\|[^}]*}}"), match.group("transfers")
                ):
                    codes.add(match2.group(1) or match2.group(2))
                if line_code.startswith("Old"):
                    codes = {"Old-" + a for a in codes}
                station = self.rail_station(codes=codes, company=company)
                stations.append(station)

            if line_code in ("C", "U"):
                RailLineBuilder(self, line).circle(*stations, forward_label="clockwise", backward_label="anticlockwise")
            else:
                forward_label, backward_label = (
                    ("eastbound", "westbound")
                    if line_code in ("X", "S", "N", "E")
                    else ("westbound", "eastbound")
                    if line_code in ("L", "W")
                    else ("southbound", "northbound")
                    if line_code in ("Z", "B", "E", "S", "J", "H")
                    else ("outbound", "inbound")
                    if not line_code.startswith("Old")
                    else (None, None)
                )
                RailLineBuilder(self, line).connect(
                    *stations, forward_label=forward_label, backward_label=backward_label
                )

            rich.print(RESULT + f"MRT {line_code} has {len(stations)} stations")
        self.save_to_cache(config, self.g)
