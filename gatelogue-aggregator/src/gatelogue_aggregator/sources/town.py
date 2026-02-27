import gatelogue_types as gt
import pandas as pd

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.source import Source


class TownList(Source):
    name = "MRT Town List"
    df: pd.DataFrame

    def prepare(self, config: Config):
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
        self.df = pd.concat((df1, df2))

    def build(self, config: Config):
        for _, row in self.df.iterrows():
            if pd.isna(row["Town Name"]):
                continue
            gt.Town.create(
                self.conn,
                self.priority,
                name=row["Town Name"],
                rank=row["Town Rank"]
                if row["Town Name"] != "Arisa"
                else "Unranked"
                if pd.isna(row["Town Rank"])
                else "Premier",
                mayor=row["Mayor"] if pd.notna(row["Mayor"]) else "MRT Staff",
                deputy_mayor=None
                if not row["Deputy Mayor"] or pd.isna(row["Deputy Mayor"])
                else row["Deputy Mayor"],
                world=row["World"],
                coordinates=None if pd.isna(row["X"]) else (row["X"], row["Z"]),
            )

        gt.Town.create(
            self.conn,
            self.priority,
            name="Central City",
            rank="Community",
            mayor="MRT Staff",
            deputy_mayor=None,
            world="New",
            coordinates=(0, 0),
        )
