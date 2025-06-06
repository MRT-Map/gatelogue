import difflib
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusLineBuilder, BusSource, BusStop


class CCC(BusSource):
    name = "MRT Wiki (Bus, Caravacan Caravan Company)"
    priority = 1

    def build(self, config: Config):
        company = BusCompany.new(self, name="Caravacan Caravan Company")
        stop_names = []

        text = get_wiki_text("Caravacan Caravan Company", config)
        started = False
        line = None

        for ln in text.split("\n"):
            if not started:
                if "Routes" in ln:
                    started = True
                continue
            if ln.strip() == "":
                continue

            line_code = ln.split(" ")[0]
            if line_code.isdigit():
                line = BusLine.new(self, code=line_code, company=company, name=line_code, colour="#800")

            stops = []
            for stn in ln.removeprefix(line_code).split("--"):
                name = stn.split("(")[0].strip()
                if not name:
                    continue
                stop_names.append(name)
                stop = BusStop.new(self, codes={name}, name=name, company=company)
                stops.append(stop)

            if len(stops) == 0:
                continue

            BusLineBuilder(self, line).connect(*stops)

        ###

        names = []
        for warp in warps(uuid.UUID("7adc9642-5f67-4264-88e3-3c8bd93261c0"), config):
            if not warp["name"].startswith("CCC"):
                continue

            warp_name = warp["name"].split("_")[1]
            name = {"JuanCarlosI": "Caravaca Airport", "MWAirport2": "Miu Wan Airport Terminal 2"}.get(
                warp_name, difflib.get_close_matches(warp_name, stop_names, 1, 0.0)[0]
            )
            if name in names:
                continue

            BusStop.new(self, codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
