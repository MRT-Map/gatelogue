import uuid
from pathlib import Path

import pandas as pd

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url, warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class RaiLinQWarp(RailSource):
    name = "MRT Warp API (Rail, RaiLinQ)"
    priority = 1

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        RailContext.__init__(self)
        Source.__init__(self)

        company = self.rail_company(name="RaiLinQ")

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

        d = dict(zip(df["Warp"], df["Name"], strict=False))

        names = []
        for warp in warps(uuid.UUID("1143017d-0f09-4b33-afdd-e5b9eb76797c"), cache_dir, timeout):
            if warp["name"] not in d or (name := d[warp["name"]]) in names:
                continue
            self.rail_station(codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
