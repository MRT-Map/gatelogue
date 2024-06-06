import re
import uuid
from pathlib import Path

import pandas as pd

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, warps, get_url
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.rail import RailSource, RailContext


class RaiLinQWarp(RailSource):
    name = "MRT Warp API (Rail, RaiLinQ)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.company(name="RaiLinQ")

        get_url(
            "https://docs.google.com/spreadsheets/d/18VPaErIgb0zOS7t8Sb4x_QwV09zFkeCM6WXL1uvIb1s/export?format=csv&gid=0",
            cache_dir / "railinq",
            timeout=timeout,
        )
        df = pd.read_csv(cache_dir / "railinq", header=1)
        df.rename(
            columns={
                "Unnamed: 1": "Name",
                "Unnamed: 2": "Warp",
            },
            inplace=True,
        )

        d = {warp: name for warp, name in zip(df["Warp"], df["Name"])}

        names = []
        for warp in warps(uuid.UUID("1143017d-0f09-4b33-afdd-e5b9eb76797c"), cache_dir, timeout):
            if warp["name"] not in d or (name := d[warp["name"]]) in names:
                continue
            self.station(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
