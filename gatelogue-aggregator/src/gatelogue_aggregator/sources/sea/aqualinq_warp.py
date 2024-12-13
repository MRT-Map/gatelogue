import uuid

import pandas as pd

from gatelogue_aggregator.downloader import get_url, warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaSource, SeaStop
from gatelogue_aggregator.types.source import Source


class AquaLinQWarp(SeaSource):
    name = "MRT Warp API (Sea, AquaLinQ)"
    priority = 0

    def __init__(self, config: Config):
        SeaSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = SeaCompany.new(self, name="AquaLinQ")

        get_url(
            "https://docs.google.com/spreadsheets/d/18VPaErIgb0zOS7t8Sb4x_QwV09zFkeCM6WXL1uvIb1s/export?format=csv&gid=1793169664",
            config.cache_dir / "aqualinq",
            timeout=config.timeout,
        )
        df = pd.read_csv(config.cache_dir / "aqualinq", header=None)
        df.rename(
            columns={
                0: "Name",
                1: "Warp1",
                2: "Warp2",
            },
            inplace=True,
        )

        d = {
            (w1 if str(w1) != "nan" else w2): n.split("(")[0].replace(",", "").strip()
            for n, w1, w2 in zip(df["Name"], df["Warp1"], df["Warp2"], strict=False)
            if not (str(n).startswith("AQ") or str(n) == "nan")
        }
        d["AQ300ENCI"] = "Encinitas Embarcadero International Seaport"
        d["AQ1200RELAXE"] = "Relaxation Islands"
        d["AQ1600TWEEB"] = "Tweebuffelsmeteenskootmorsdoodgeskietfontein"
        d["AQ1300CARDS"] = "Cardinal Bay"
        d["AQ900ONEM"] = "Onemalu Moku Uopa Regional Pier"

        names = []
        for warp in warps(uuid.UUID("1143017d-0f09-4b33-afdd-e5b9eb76797c"), config):
            if warp["name"] not in d or (name := d[warp["name"]]) in names:
                continue
            SeaStop.new(self, codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)

        self.save_to_cache(config, self.g)
