from pathlib import Path
from typing import Literal
import uuid

import rich

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.node.bus import BusCompany, BusLine, BusSource, BusStop
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaSource, SeaStop
from gatelogue_aggregator.types.source import Source


class Yaml2Source(RailSource, BusSource, SeaSource):
    name = "MRT Wiki (Rail, SEAT)"
    priority = 1

    C: type[RailCompany | BusCompany | SeaCompany]
    L: type[RailLine | BusLine | SeaLine]
    S: type[RailStation | BusStop | SeaStop]

    def __init__(self, config: Config, file_path: Path):
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        with file_path.open() as f:
            file = yaml

        company = self.C.new(self, name="SEAT")
        station_names = []

        html = get_wiki_html("Seoland Economically/Ecologically Advanced Transit", config)
        first_seen = False
        for h3 in html.find_all("h3"):
            line_name: str = h3.find("span", class_="mw-headline").string
            if not first_seen:
                if "Savagebite" in line_name:
                    first_seen = True
                else:
                    continue

            line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp", colour="#000080")

            line_table = h3.find_next("table")
            if line_table is None or line_table.caption is None or "Line" not in line_table.caption.string:
                continue

            stations = []
            for tr in line_table("tr")[1:]:
                if "Open" not in next(tr("td")[3].strings):
                    continue
                name = tr("td")[1].string.strip().removesuffix(" Station")

                station_names.append(name)
                station = RailStation.new(self, codes={name}, name=name, company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"SEAT Line {line_name} has {len(stations)} stations")

        ###

        names = []
        for warp in warps(uuid.UUID("02625b8c-b2a5-4999-8756-855831976411"), config):
            if not warp["name"].lower().startswith("seatr"):
                continue
            warp_name = warp["name"][5:]
            name = {"niz": "New Izumo", "newgen": "New Genisys"}.get(
                warp_name,
                difflib.get_close_matches(warp_name, station_names, 1, 0.0)[0],
            )
            if name in names or name is None:
                continue

            RailStation.new(self, codes={name}, company=company, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)

        self.save_to_cache(config, self.g)
