import itertools
import re
from pathlib import Path

import rich

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.rail import Connection, RailContext, RailSource, Station
from gatelogue_aggregator.utils import search_all


class BluRail(RailSource):
    name = "MRT Wiki (Rail, BluRail)"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.company(name="BluRail")

        for line_code in (
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "11",
            "12",
            "14",
            "15",
            "16",
            "20",
            "23",
            "1X",
            "2X",
            "3X",
            "7X",
            "14X",
            "AA",
            "AB",
            "BS",
            "CS",
            "ES",
            "FC",
            "FY",
            "GC",
            "GS",
            "IS",
            "JC",
            "LC",
            "NF",
            "NI",
            "OP",
            "OS",
            "PS",
            "PX",
            "RC",
            "SF",
            "SN",
            "TS",
            "WC",
            "WS",
        ):
            wiki = get_wiki_text(f"{line_code} (BluRail line)", cache_dir, timeout)
            line_name = re.search(r"\| linelong = (.*)\n", wiki).group(1)
            line = self.line(code=line_code, name=line_name, company=company, mode="warp")

            stations = []
            for result in search_all(re.compile(r"\|-\n\|(?!<s>)(?P<code>.*?)\n\|(?P<name>.*?)\n"), wiki):
                station = self.station(codes={result.group("code")}, name=result.group("name"), company=company)
                stations.append(station)

            for s1, s2 in itertools.pairwise(stations):
                s1: Station
                s2: Station
                s1.connect(self, s2, key=Connection(line=line.id))

            rich.print(f"[green]  BluRail Line {line_code} has {len(stations)} stations")
