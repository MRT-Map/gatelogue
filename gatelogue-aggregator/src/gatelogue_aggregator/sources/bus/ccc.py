import difflib
import re
import uuid

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.source import BusSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_text


class CCC(BusSource):
    name = "MRT Wiki (Bus, Caravacan Caravan Company)"
    text: str

    def prepare(self, config: Config):
        self.text = get_wiki_text("Caravacan Caravan Company", config)

    def build(self, config: Config):
        company = self.company(name="Caravacan Caravan Company")
        stop_names = []

        line = None
        stops = []

        for ln in self.text.split("\n"):
            if (match := re.search(r"'''Line (.*?)'''", ln)) is not None:
                line_code = match.group(1)
                line = self.line(code=line_code, company=company, name=line_code, colour="#800")
                continue
            if ln.strip() == "" and line is not None:
                if len(stops) != 0:
                    builder = self.builder(line)
                    builder.add(*stops)
                    builder.connect()
                line = None
                stops.clear()
                continue
            if line is None:
                continue

            name = ln.removeprefix("* ")
            stop = self.stop(codes={name}, name=name, company=company)
            stops.append(stop)
            stop_names.append(name)

        ###

        names = []
        for warp in warps(uuid.UUID("7adc9642-5f67-4264-88e3-3c8bd93261c0"), config):
            if not warp["name"].startswith("CCC"):
                continue

            warp_name = warp["name"].split("_")[1]
            name = {
                "JuanCarlosI": "Caravaca - Juan Carlos I",
                "MWAirport": "Miu Wan TTL T1",
                "MWAirport2": "Miu Wan TTL T2",
                "EFAirfield": "Ellerton Fosby Airport",
                "ottia": "Ottia Islands",
            }.get(warp_name, difflib.get_close_matches(warp_name, stop_names, 1, 0.0)[0])
            print(warp_name, name)
            if name in names:
                continue

            self.stop(codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
