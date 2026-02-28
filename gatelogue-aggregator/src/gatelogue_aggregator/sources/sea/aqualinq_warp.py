import pandas as pd

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.source import SeaSource
from gatelogue_aggregator.sources.warp_api import WarpAPI


class AquaLinQWarp(SeaSource):
    name = "MRT Warp API (Sea, AquaLinQ)"
    d: dict[str, str]

    def prepare(self, config: Config):
        get_url(
            "https://docs.google.com/spreadsheets/d/18VPaErIgb0zOS7t8Sb4x_QwV09zFkeCM6WXL1uvIb1s/export?format=csv&gid=1793169664",
            "aqualinq",
            config,
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
            (w1 if pd.notna(w1) else w2): n.split("(")[0].replace(",", "").strip()
            for n, w1, w2 in zip(df["Name"], df["Warp1"], df["Warp2"], strict=False)
            if not (str(n).startswith("AQ") or pd.isna(n))
        }
        d["AQ300ENCI"] = "Encinitas Embarcadero International Seaport"
        d["AQ1200RELAXE"] = "Relaxation Islands"
        d["AQ1600TWEEB"] = "Tweebuffelsmeteenskootmorsdoodgeskietfontein"
        d["AQ1300CARDS"] = "Cardinal Bay"
        d["AQ900ONEM"] = "Onemalu Moku Uopa Regional Pier"
        d["AQ1600MORA"] = "Moramoa Central"
        d["AQ1000NIWEN"] = "Niwen"
        self.d = d

    def build(self, config: Config):
        company = self.company(name="AquaLinQ")

        names = []
        for warp in WarpAPI.from_user("1143017d-0f09-4b33-afdd-e5b9eb76797c"):
            if warp.name not in self.d or (name := self.d[warp.name]) in names:
                continue
            self.stop(codes={name}, company=company, name=name, world="New", coordinates=warp.coordinates)
            names.append(name)
