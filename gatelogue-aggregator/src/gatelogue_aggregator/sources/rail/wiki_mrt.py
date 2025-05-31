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


class WikiMRT(RailSource):
    name = "MRT Wiki (Rail, MRT)"
    priority = 0

    def build(self, config: Config):
        company = RailCompany.new(self, name="MRT")

        for line_code, line_name, line_colour in (
            ("A", "MRT Arctic Line", "#00FFFF"),
            ("C", "MRT Circle Line", "#5E5E5E"),
            ("D", "MRT Desert Line", "#9437FF"),
            ("E", "MRT Eastern Line", "#10D20F"),
            ("F", "MRT Forest Line", "#0096FF"),
            ("H", "MRT Savannah Line", "#5B7F00"),
            ("I", "MRT Island Line", "#FF40FF"),
            ("J", "MRT Jungle Line", "#4C250D"),
            ("L", "MRT Lakeshore Line", "#9B95BC"),
            ("M", "MRT Mesa Line", "#FF8000"),
            ("N", "MRT Northern Line", "#0433FF"),
            ("O", "MRT Oasis Line", "#021987"),
            ("P", "MRT Plains Line", "#008E00"),
            ("R", "MRT Rose Line", "#FE2E9A"),
            ("S", "MRT Southern Line", "#FFFA28"),
            ("T", "MRT Taiga Line", "#915001"),
            ("U", "MRT Union Line", "#2B2C35"),
            ("V", "MRT Valley Line", "#FF8AD8"),
            ("W", "MRT Western Line", "#FF0000"),
            ("X", "MRT Expo Line", "#000000"),
            ("XM", "MRT Marina Shuttle", "#000000"),
            ("Z", "MRT Zephyr Line", "#EEEEEE"),
            ("Old-R", "MRT Red Line", "#FF0000"),
            ("Old-B", "MRT Blue Line", "#0000FF"),
            ("Old-Y", "MRT Yellow Line", "#FFFF00"),
            ("Old-G", "MRT Green Line", "#00FF00"),
            ("Old-O", "MRT Orange Line", "#FF8000"),
        ):
            text = get_wiki_text(line_name, config)
            line = RailLine.new(self, code=line_code, company=company, name=line_name, colour=line_colour)

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
                station = RailStation.new(self, codes=codes, company=company)
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
        
