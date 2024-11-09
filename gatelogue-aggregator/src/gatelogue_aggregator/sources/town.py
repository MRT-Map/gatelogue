import pandas as pd

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.town import TownContext, TownSource
from gatelogue_aggregator.types.source import Source


class TownList(TownSource):
    name = "MRT Town List"
    priority = 0

    def __init__(self, config: Config):
        cache1 = config.cache_dir / "town-list1"
        cache2 = config.cache_dir / "town-list2"
        TownContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        get_url(
            "https://docs.google.com/spreadsheets/d/1JSmJtYkYrEx6Am5drhSet17qwJzOKDI7tE7FxPx4YNI/export?format=csv&gid=0",
            cache1,
            timeout=config.timeout,
        )
        df1 = pd.read_csv(cache1)
        df1["World"] = "New"

        get_url(
            "https://docs.google.com/spreadsheets/d/1JSmJtYkYrEx6Am5drhSet17qwJzOKDI7tE7FxPx4YNI/export?format=csv&gid=1533469138",
            cache2,
            timeout=config.timeout,
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
                coordinates=None if str(row["X"]) == "nan" else (row["X"], row["Z"]),
            )

        self.save_to_cache(config, self.g)
