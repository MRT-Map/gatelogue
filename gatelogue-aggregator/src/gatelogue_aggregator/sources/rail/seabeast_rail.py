import difflib
import re
import uuid

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_text


class SeabeastRail(RailSource):
    name = "MRT Wiki (Rail, Seabeast Rail)"
    text: str
    warps: list[dict]

    def prepare(self, config: Config):
        self.text = get_wiki_text("Seabeast Rail", config)
        self.warps = list(warps(uuid.UUID("99197ab5-4a78-4e99-b43b-fdf1e04ada1d"), config))

    def build(self, config: Config):
        company = self.company(name="Seabeast Rail")
        line = self.line(code="Green Line", company=company, name="Green Line", colour="green")
        station_names = []

        builder = self.builder(line)
        for match in re.finditer(
            re.compile(r"""\| style="background:green; border:none; " \|.*?
\| style ="border:none; " \| • ([^(\n]*)"""),
            self.text,
        ):
            name = match.group(1)
            station_names.append(name)
            builder.add(self.station(codes={name}, name=name, company=company))

        builder.connect()

        ###

        names = []
        for warp in self.warps:
            if not warp["name"].startswith("SBR"):
                continue

            warp_name = warp["name"][6:]
            name = {"NSV": "Neue Savanne"}.get(
                warp_name,
                difflib.get_close_matches(warp_name, station_names, 1, 0.0)[0],
            )
            if name in names:
                continue

            self.station(codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
