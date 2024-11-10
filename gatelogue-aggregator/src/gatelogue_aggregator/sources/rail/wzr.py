import re

import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html, get_wiki_text
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


class WZR(RailSource):
    name = "MRT Wiki (Rail, West Zeta Rail)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="West Zeta Rail")

        html = get_wiki_html("List of West Zeta Rail lines", config)

        for table in html.find_all("table"):
            if "Code" not in table.th.string:
                continue
            span = table.previous_sibling.previous_sibling.find(
                "span", class_="mw-headline"
            ) or table.previous_sibling.previous_sibling.previous_sibling.previous_sibling.find(
                "span", class_="mw-headline"
            )
            if (result := re.search(r"Line (?P<code>.*?) - (?P<name>.*)|(?P<name2>[^(]*)", span.string)) is None:
                continue
            line_name = result.group("name") or result.group("name2")
            line_code = result.group("code") or line_name
            line = RailLine.new(self, code=str(line_code).strip(), name=str(line_name).strip(), company=company)

            stations = []
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:  # noqa: PLR2004
                    continue
                if tr("td")[3].string.strip() == "Planned":
                    continue
                code = str(tr("td")[0].string).strip()
                name = "".join(tr("td")[1].strings).strip().rstrip("*")
                station = RailStation.new(self, codes={code}, name=name, company=company)
                stations.append(station)

            RailLineBuilder(self, line).connect(*stations)
            rich.print(RESULT + f"WZR Line {line_code} has {len(stations)} stations")

        for line_code, line_name in (
            ("2", "Northmist Line"),
            ("4", "Genso Line"),
            ("10", "Centrale Line"),
        ):
            wiki = get_wiki_text(line_name, config)
            line = RailLine.new(self, code=line_code, name=line_name, company=company)

            stations = []
            for result in search_all(
                re.compile(
                    r"(?:\[\[(?:[^|]*\|)?(?P<name1>[^|]*)]]|{{stl\|WZR\|(?P<name2>[^|]*)}}) *\|\| *(?P<code>\w\w\w)"
                ),
                wiki,
            ):
                code = result.group("code").upper()
                name = (result.group("name1") or result.group("name2")).strip()
                station = RailStation.new(self, codes={code}, name=name, company=company)
                stations.append(station)

            RailLineBuilder(self, line).connect(*stations)
            rich.print(RESULT + f"WZR Line {line_code} has {len(stations)} stations")

        wiki = get_wiki_text("Ismael Line", config)
        line = RailLine.new(self, code="8", name="Ismael Line", company=company)

        stations = []
        for result in search_all(
            re.compile(r"\[\[(?:[^|]*\|)?(?P<name>[^|]*)]] *\|\| *(?P<code>\w\w\w) .*\|\|.*\|\|(?! *Planned)"), wiki
        ):
            code = result.group("code").upper()
            name = result.group("name").strip()
            station = RailStation.new(self, codes={code}, name=name, company=company)
            stations.append(station)

        RailLineBuilder(self, line).connect(*stations)
        rich.print(RESULT + f"WZR Line 8 has {len(stations)} stations")

        self.save_to_cache(config, self.g)
