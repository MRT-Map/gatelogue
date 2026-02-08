import re

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_text


class WikiMRT(RailSource):
    name = "MRT Wiki (Rail, MRT)"
    lines: list[tuple[str, str, str, str]] = []

    def prepare(self, config: Config):
        for line_code, line_name, line_colour in (
            ("A", "MRT Arctic Line", "#00FFFF"),
            ("B", "MRT Beach Line", "#EEDB95"),
            ("C", "MRT Circle Line", "#5E5E5E"),
            ("D", "MRT Desert Line", "#9437FF"),
            ("E", "MRT Eastern Line", "#10D20F"),
            ("F", "MRT Forest Line", "#0096FF"),
            ("G", "MRT Garden Line", "#8A9A5B"),
            ("H", "MRT Savannah Line", "#5B7F00"),
            ("I", "MRT Island Line", "#FF40FF"),
            ("J", "MRT Jungle Line", "#4C250D"),
            ("K", "MRT Knight Line", "#74A181"),
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
            ("Y", "MRT Yeti Line", "#ADD8E6"),
            ("Z", "MRT Zephyr Line", "#EEEEEE"),
            ("Old-R", "MRT Red Line", "#FF0000"),
            ("Old-B", "MRT Blue Line", "#0000FF"),
            ("Old-Y", "MRT Yellow Line", "#FFFF00"),
            ("Old-G", "MRT Green Line", "#00FF00"),
            ("Old-O", "MRT Orange Line", "#FF8000"),
        ):
            self.lines.append((line_code, line_name, line_colour, get_wiki_text(line_name, config)))

    def build(self, config: Config):
        company = self.company(name="MRT")

        for line_code, line_name, line_colour, text in self.lines:
            line = self.line(code=line_code, company=company, name=line_name, colour=line_colour, mode="cart")
            builder = self.builder(line)
            for match in re.finditer(
                re.compile(r"{{station\|open\|[^|]*?\|(?:c=white\|)?(?P<code>[^|]*?)\|(?P<transfers>.*?)}}\s*\n"), text
            ):
                codes = {match.group("code")}
                for match2 in re.finditer(
                    re.compile(r"{{st/n\|[^}]*\|([^}]*)}}|{{s\|([^}]*)\|[^}]*}}"), match.group("transfers")
                ):
                    new_code = match2.group(1) or match2.group(2)
                    if new_code == "L3X":
                        continue
                    codes.add(new_code)
                if line_code.startswith("Old"):
                    codes = {"Old-" + a for a in codes}
                builder.add(self.station(codes=codes, company=company))

            if line_code in ("C", "U"):
                builder.connect_circle(forward_direction="clockwise", backward_direction="anticlockwise")
            else:
                forward_label, backward_label = (
                    ("eastbound", "westbound")
                    if line_code in ("X", "S", "N", "E", "R")
                    else ("westbound", "eastbound")
                    if line_code in ("L", "O", "W", "Y")
                    else ("southbound", "northbound")
                    if line_code in ("Z", "B", "E", "S", "J", "H")
                    else ("northbound", "southbound")
                    if line_code in ("K",)
                    else ("outbound", "inbound")
                    if not line_code.startswith("Old")
                    else (None, None)
                )
                builder.connect(forward_direction=forward_label, backward_direction=backward_label)
