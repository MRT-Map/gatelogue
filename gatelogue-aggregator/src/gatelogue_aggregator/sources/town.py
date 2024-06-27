from pathlib import Path

import pandas as pd

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.node.town import TownSource, TownContext


class TownList(TownSource):
    name = "MRT Town List"
    priority = 0

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        cache1 = cache_dir / "town-list1"
        cache2 = cache_dir / "town-list2"
        TownContext.__init__(self)
        Source.__init__(self)

        get_url(
            "https://docs.google.com/spreadsheets/d/1JSmJtYkYrEx6Am5drhSet17qwJzOKDI7tE7FxPx4YNI/export?format=csv&gid=0",
            cache1,
            timeout=timeout,
        )
        df1 = pd.read_csv(cache1)
        df1["World"] = "New"

        get_url(
            "https://docs.google.com/spreadsheets/d/1JSmJtYkYrEx6Am5drhSet17qwJzOKDI7tE7FxPx4YNI/export?format=csv&gid=1533469138",
            cache2,
            timeout=timeout,
        )
        df2 = pd.read_csv(cache2)
        df2["World"] = "Old"
        df2["Town Rank"] = "Unranked"

        for _, row in pd.concat((df1, df2)).iterrows():
            if not row["Town Name"]:
                continue
            self.town(
                name=row["Town Name"],
                rank=row["Town Rank"] if row["Town Name"] != "Arisa" else "Premier",
                mayor=row["Mayor"],
                deputy_mayor=None if not row["Deputy Mayor"] or row["Deputy Mayor"] == "-" else row["Deputy Mayor"],
                world=row["World"],
                coordinates=None if row["X"] == "nan" else (row["X"], row["Z"]),
            )
