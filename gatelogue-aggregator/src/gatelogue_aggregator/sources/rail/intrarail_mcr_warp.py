import itertools
import re
import uuid
from pathlib import Path

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class IntraRailMCRWarp(RailSource):
    name = "MRT Warp API (Rail, IntraRail MCR)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="IntraRail")

        html = get_wiki_html("", cache_dir, timeout, old_id=203396)

        code2name = {}
        for table in html.find_all("table"):
            if "Code" not in table("th")[1].string:
                continue

            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:  # noqa: PLR2004
                    continue
                code = str(tr("td")[1].span.span.string).strip()
                name = "".join(tr("td")[2].strings).strip()
                code2name[code] = name.replace(" -  ", " ").replace(" - ", " ")

        names = []
        for warp in itertools.chain(
            warps(uuid.UUID("16990807-9df4-4bde-89b7-efee9836b7a6"), cache_dir, timeout),
            warps(uuid.UUID("928761c5-d95f-4e16-8761-624dada75dc2"), cache_dir, timeout),
        ):
            if not warp["name"].startswith("MCR") or len(warp["name"].split("_")) < 2:
                continue
            code = warp["name"].split("_")[1]
            if code == "OCJS":
                name = code2name["OCJS-" + warp["name"].split("_")[2]]
            elif code in code2name:
                name = code2name[code]
            self.rail_station(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
