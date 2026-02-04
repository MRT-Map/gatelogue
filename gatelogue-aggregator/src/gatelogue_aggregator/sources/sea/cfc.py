import difflib
import uuid

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.source import SeaSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_text


class CFC(SeaSource):
    name = "MRT Wiki (Sea, Caravacan Floaty Company)"
    text: str
    warps: list[dict]

    def prepare(self, config: Config):
        self.text = get_wiki_text("Caravacan Floaty Company", config)
        self.warps = list(warps(uuid.UUID("7adc9642-5f67-4264-88e3-3c8bd93261c0"), config))

    def build(self, config: Config):
        company = self.company(name="Caravacan Floaty Company")
        stop_names = []

        for ln in self.text.split("\n"):
            if ". " not in ln:
                continue
            line_code, line_stations = ln.split(". ")
            if len(line_code) > 3:
                continue
            line = self.line(code=line_code, company=company, name=line_code, colour="#800")

            builder = self.builder(line)
            for stn in line_stations.split("--"):
                name = stn.strip(" '")
                stop_names.append(name)
                builder.add(self.stop(codes={name}, name=name, company=company))

            builder.connect()

        ###

        names = []
        for warp in self.warps:
            if not warp["name"].startswith("CFC"):
                continue

            warp_name = warp["name"].split("_")[1]
            name = {
                ",": ",",
                "DeadbushW": "Deadbush Weezerville",
                "Leknes": "Leknes",
                "NSouthport": "New Southport",
                "NBakersville": "New Bakersville",
                "NSeriade": "Nueva Seriadé",
                "Erzville": "Erzville Central",
            }.get(warp_name, difflib.get_close_matches(warp_name, stop_names, 1, 0.0)[0])
            if name in names:
                continue

            self.stop(codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
