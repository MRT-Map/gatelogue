import itertools
import re
from pathlib import Path

import msgspec
import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.rail import Connection, RailContext, RailSource, Station
from gatelogue_aggregator.utils import search_all


class WikiMRT(RailSource):
    name = "MRT Wiki (Rail, MRT)"
    priority = -1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.company(name="MRT")

        for line_code, line_name in (
            ("A", "MRT Arctic Line"),
            ("C", "MRT Circle Line"),
            ("D", "MRT Desert Line"),
            ("E", "MRT Eastern Line"),
            ("F", "MRT Forest Line"),
            ("H", "MRT Savannah Line"),
            ("I", "MRT Island Line"),
            ("J", "MRT Jungle Line"),
            ("L", "MRT Lakeshore Line"),
            ("M", "MRT Mesa Line"),
            ("N", "MRT Northern Line"),
            ("O", "MRT Oasis Line"),
            ("P", "MRT Plains Line"),
            ("R", "MRT Rose Line"),
            ("S", "MRT Southern Line"),
            ("T", "MRT Taiga Line"),
            ("U", "MRT Union Line"),
            ("V", "MRT Valley Line"),
            ("W", "MRT Western Line"),
            ("X", "MRT Expo Line"),
            ("Z", "MRT Zephyr Line"),
            ("Old-R", "MRT Red Line"),
            ("Old-B", "MRT Blue Line"),
            ("Old-Y", "MRT Yellow Line"),
            ("Old-G", "MRT Green Line"),
            ("Old-O", "MRT Orange Line"),
        ):
            text = get_wiki_text(line_name, cache_dir, timeout)
            line = self.line(code=line_code, company=company, name=line_name)

            stations = []
            for match in search_all(
                re.compile(r"{{station\|open\|[^|]*?\|(?P<code>[^|]*?)\|(?P<transfers>.*?)}}\s*\n"), text
            ):
                codes = {match.group("code")}
                for match2 in search_all(
                    re.compile(r"{{st/n\|[^}]*\|([^}]*)}}|{{s\|([^}]*)\|[^}]*}}"), match.group("transfers")
                ):
                    codes.add(match2.group(1) or match2.group(2))
                if line_code.startswith("Old"):
                    codes = {"Old-" + a for a in codes}
                station = self.station(codes=codes, company=company)
                stations.append(station)

            for s1, s2 in itertools.pairwise(stations):
                s1: Station
                s2: Station
                s1.connect(self, s2, key=Connection(line=line.id))
            if line_code in ("C", "U"):
                stations[0].connect(self, stations[-1], key=Connection(line=line.id))

            rich.print(f"[green]  MRT {line_code} has {len(stations)} stations")
