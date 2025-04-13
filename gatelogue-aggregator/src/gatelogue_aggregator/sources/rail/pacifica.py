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


class Pacifica(RailSource):
    name = "MRT Wiki (Rail, Pacifica)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="Pacifica")

        text = get_wiki_text("Pacifica", config)
        for match in search_all(
            re.compile(r"(?s){\| class=\"wikitable\".*?\n\|\+\n!(?P<name>.*?)\n\|-\n(?P<stations>.*?)\n\|}"), text
        ):
            line_name = match.group("name")
            if "Planned" in line_name or "Colwyn" in line_name:
                continue
            line = RailLine.new(
                self, code=line_name, name=line_name, company=company, mode="traincart", colour="#008080"
            )

            stations = []
            for name in match.group("stations").split("\n|-\n"):
                if "No Station" in name:
                    continue
                name = name.removeprefix("|")
                if "*" in name:
                    name = name.strip("*'")

                name = {
                    "Janghwa": "Janghwa Northern Union",
                    "Janghwa Northern": "Janghwa Northern Union",
                    "Utopia": "Utopia - AFK Transit Hub",
                    "Espil": "Espil - Ricola Terminal",
                    "Espil - Atvix Centre": "Espil - Ricola Terminal",
                    "Evella": "Evella Airport",
                    "Lacelde": "Laclede",
                    "Lacelde East": "Laclede East",
                    "West Calbar": "West Calbar - Forest Landing",
                    "Ilirea - SunrisePark - South": "Ilirea - Sunrise Park - South",
                    "Pasadena - Voltsphere Union Sta.": "Pasadena - Voltsphere Union",
                }.get(name, name)

                station = RailStation.new(self, codes={name}, name=name, company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"Pacifica {line_name} has {len(stations)} stations")

        self.save_to_cache(config, self.g)
