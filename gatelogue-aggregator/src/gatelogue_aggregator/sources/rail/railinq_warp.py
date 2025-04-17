import uuid

import pandas as pd

from gatelogue_aggregator.downloader import get_url, warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.source import Source


class RaiLinQWarp(RailSource):
    name = "MRT Warp API (Rail, RaiLinQ)"
    priority = 0

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="RaiLinQ")

        get_url(
            "https://docs.google.com/spreadsheets/d/18VPaErIgb0zOS7t8Sb4x_QwV09zFkeCM6WXL1uvIb1s/export?format=csv&gid=0",
            config.cache_dir / "railinq",
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        df = pd.read_csv(config.cache_dir / "railinq", header=1)
        df.rename(
            columns={
                "Unnamed: 1": "Name",
                "Unnamed: 2": "Warp",
            },
            inplace=True,
        )

        d = dict(zip(df["Warp"], df["Name"], strict=False))

        rename = {
            "AT Western Transportation Hub": "Achowalogen Takachsin Western Transportation Hub",
            "Downtown AT/Covina": "Downtown Achowalogen Takachsin/Covina",
            "AT Suburb": "Achowalogen Takachsin Suburb",
            "Vekta & Xandar": "Vekta And Xandar",
            "Espil North/East": "Espil North-East",
            "Summerville-Ulfthorp": "Summerville - Ulfthorp",
            "Ilirea Cascadia": "Ilirea ITC",
            "Verdantium Fenwick Square": "Fenwick Central",
            "Vergil IKEA": "Covina IKEA",
            "savacaci": "Savacaci",
            "Orio&Waterville": "Orio & Waterville",
        }

        names = ["Amestris West", "Washingcube East", "Washingcube West"]
        for warp in warps(uuid.UUID("1143017d-0f09-4b33-afdd-e5b9eb76797c"), config):
            if warp["name"] not in d or (name := rename.get(d[warp["name"]], d[warp["name"]])) in names:
                continue

            RailStation.new(
                self, codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"])
            )
            names.append(name)
        self.save_to_cache(config, self.g)
