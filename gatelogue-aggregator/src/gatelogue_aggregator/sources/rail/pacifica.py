import re

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.utils import search_all


class Pacifica(RailSource):
    name = "MRT Wiki (Rail, Pacifica)"
    text: str

    def prepare(self, config: Config):
        self.text = get_wiki_text("Pacifica", config)

    def build(self, config: Config):
        company = self.company(name="Pacifica")

        for match in search_all(
            re.compile(r"(?s){\| class=\"wikitable\".*?\n\|\+\n!(?P<name>.*?)\n\|-\n(?P<stations>.*?)\n\|}"), self.text
        ):
            line_name = match.group("name")
            if "Planned" in line_name or "Colwyn" in line_name:
                continue
            line = self.line(code=line_name, name=line_name, company=company, mode="traincarts", colour="#008080")

            builder = self.builder(line)
            for name in match.group("stations").split("\n|-\n"):
                if "No Station" in name or "(planned)" in name:
                    continue
                name = name.removeprefix("|")  # noqa: PLW2901
                if "*" in name:
                    name = name.strip("*'")  # noqa: PLW2901
                if name.strip() == "":
                    continue

                name = {  # noqa: PLW2901
                    "Utopia": "Utopia - AFK Transit Hub",
                    "Espil": "Espil - Ricola Terminal",
                    "Espil - Atvix Centre": "Espil - Ricola Terminal",
                    "Evella": "Evella Airport",
                    "Lacelde": "Laclede",
                    "Lacelde East": "Laclede East",
                    "West Calbar": "West Calbar - Forest Landing",
                    "Ilirea - SunrisePark - South": "Ilirea - Sunrise Park - South",
                    "Pasadena - Voltsphere Union Sta.": "Pasadena - Voltsphere Union",
                    "Blueberry City": "Blackberry City",
                    "Central City - Park Terminal (Spawn)": "Central City - Park Terminal",
                    "Blackfriars": "Blackfriars - Huxley Square",
                }.get(name, name)

                builder.add(self.station(codes={name}, name=name, company=company))

            builder.connect()
