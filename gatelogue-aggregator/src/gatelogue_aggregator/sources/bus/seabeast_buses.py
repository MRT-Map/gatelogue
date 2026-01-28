import difflib
import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.source import BusSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.utils import search_all


class SeabeastBuses(BusSource):
    name = "MRT Wiki (Bus, Seabeast Buses)"
    text: str

    def prepare(self, config: Config):
        self.text = get_wiki_text("Seabeast Buses", config)

    def build(self, config: Config):
        company = self.company(name="Seabeast Buses")
        stop_names = {}

        for match in search_all(
            re.compile(r"""\|-
\| style="background:(?P<col>.*?);.*?
\|(?P<code>.*?)
\|(?P<origin>.*?)
\|.*?
\|(?P<dests>.*?)
\| style="background:green"""),
            self.text,
        ):
            line_code = match.group("code")
            line_colour = match.group("col")
            line = self.line(
                code=line_code,
                company=company,
                name=line_code,
                colour="#eee" if line_colour == "white" else line_colour,
            )

            builder = self.builder(line)
            for n in (match.group("origin"), *match.group("dests").split(",")):
                name = n.strip()
                stop_names.setdefault(line_code, []).append(name)
                builder.add(self.stop(codes={name}, name=name, company=company))

            if len(builder.station_list) == 0:
                continue
            builder.connect()

        ###

        names = []
        for warp in warps(uuid.UUID("99197ab5-4a78-4e99-b43b-fdf1e04ada1d"), config):
            if not warp["name"].startswith("SBB"):
                continue

            warp_name = warp["name"][6:]
            name = {
                "HEN": "Hendon Coach Station",
                "HAM": "Hamblin Municipal Airport",
                "DPH": "Deadbush Pioneer-Howard Airport",
                "BAY": "Bay Point",
                "PXL": "Pixl Vinayaka International Airport",
                "CAR": "Carnoustie" if warp["name"] == "SBB023CAR" else "Caravaca-Juan Carlos I Airfield",
                "THR": "thrive",
            }.get(
                warp_name,
                next(iter(difflib.get_close_matches(warp_name, stop_names.get(warp["name"][3:6], []), 1, 0.0)), None),
            )
            if name in names or name is None:
                continue

            self.stop(codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
