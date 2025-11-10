import pandas as pd

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.town import Town, TownSource


class TownList(TownSource):
    name = "MRT Town List"
    priority = 0

    def build(self, config: Config):
        cache1 = config.cache_dir / "town-list1"
        cache2 = config.cache_dir / "town-list2"

        get_url(
            "https://docs.google.com/spreadsheets/d/1JSmJtYkYrEx6Am5drhSet17qwJzOKDI7tE7FxPx4YNI/export?format=csv&gid=0",
            cache1,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        df1 = pd.read_csv(cache1)
        df1["World"] = "New"

        get_url(
            "https://docs.google.com/spreadsheets/d/1JSmJtYkYrEx6Am5drhSet17qwJzOKDI7tE7FxPx4YNI/export?format=csv&gid=1533469138",
            cache2,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        df2 = pd.read_csv(cache2)
        df2["World"] = "Old"
        df2["Town Rank"] = "Unranked"

        for _, row in pd.concat((df1, df2)).iterrows():
            if str(row["Town Name"]) == "nan":
                continue
            Town.new(
                self,
                name=row["Town Name"],
                rank=row["Town Rank"] if row["Town Name"] != "Arisa" else "Unranked" if str(row["Town Rank"]) == "nan" else "Premier",
                mayor=row["Mayor"] if str(row["Mayor"]) != "nan" else "MRT Staff",
                deputy_mayor=None
                if not row["Deputy Mayor"] or str(row["Deputy Mayor"]) == "nan"
                else row["Deputy Mayor"],
                world=row["World"],
                coordinates=None if str(row["X"]) == "nan" else (row["X"], row["Z"]),
            )

        Town.new(
            self,
            name="Central City",
            rank="Community",
            mayor="MRT Staff",
            deputy_mayor=None,
            world="New",
            coordinates=(0, 0),
        )
