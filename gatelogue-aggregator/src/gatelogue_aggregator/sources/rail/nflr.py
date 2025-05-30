from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.utils import get_stn


class NFLR(RailSource):
    name = "MRT Wiki (Rail, nFLR)"
    priority = 1

    def build(self, config: Config):
        cache = config.cache_dir / "nflr"

        company = RailCompany.new(self, name="nFLR")

        get_url(
            "https://docs.google.com/spreadsheets/d/1ohIRZrcLZByL5feqDqgA0QeC3uwAlBKOMKxWMRTSxRw/export?format=csv&gid=1540849896",
            cache / "lines",
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        df = pd.read_csv(cache / "lines")
        lines = [
            (str(line_name), str(back), bool(w), int(gid))
            for line_name, back, w, gid in zip(df["line"], df["back"], df["w"], df["gid"], strict=False)
            if str(gid) != "nan"
        ]

        def retrieve_urls(line_name: str, gid: int):
            get_url(
                "https://docs.google.com/spreadsheets/d/1ohIRZrcLZByL5feqDqgA0QeC3uwAlBKOMKxWMRTSxRw/export?format=csv&gid="
                + str(gid),
                cache / line_name,
                timeout=config.timeout,
                cooldown=config.cooldown,
            )

        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            list(executor.map(lambda s: retrieve_urls(s[0], s[3]), lines))

        for line_name, line_colour, w, _ in lines:
            df = pd.read_csv(cache / line_name)

            d = list(zip(df["route"], df["code"], df["name"], strict=False))

            r_stations = []
            w_stations = []
            for route, code, name in d:
                code = {  # noqa: PLW2901
                    "n104": {"n104", "n203", "n300"},
                    "n203": {"n104", "n203", "n300"},
                    "n300": {"n104", "n203", "n300"},
                    "n105": {"n105", "n202"},
                    "n202": {"n105", "n202"},
                    "hzc": {"hzc", "n213"},
                    "n213": {"hzc", "n213"},
                    "frg": {"frg", "n214"},
                    "n214": {"frg", "n214"},
                }.get(code, {code})
                station = None
                if "R" in route:
                    station = station or RailStation.new(self, codes=code, company=company, name=name)
                    r_stations.append(station)
                if "W" in route and w:
                    station = station or RailStation.new(self, codes=code, company=company, name=name)
                    w_stations.append(station)

            r_line = RailLine.new(
                self,
                code=line_name,
                name=line_name,
                company=company,
                mode="warp",
                colour=line_colour,
            )

            if line_name == "R7A":
                RailLineBuilder(self, r_line).circle(
                    *r_stations,
                    forward_label="clockwise",
                    backward_label="anticlockwise",
                )
            elif line_name == "R5A":
                RailLineBuilder(self, r_line).connect(
                    *r_stations,
                    between=(None, "Deadbush Euphorial"),
                    forward_label="southbound",
                    backward_label="northbound",
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations,
                    between=("Deadbush Euphorial", "Deadbush Quarryville"),
                    forward_label="southbound",
                    backward_label="northbound CW",
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations,
                    between=(
                        "Deadbush Quarryville",
                        "Deadbush Johnston-Euphorial Airport Terminal 2",
                    ),
                    forward_label="northbound CCW",
                    backward_label="southbound",
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations,
                    get_stn(r_stations, "Deadbush Karaj Expo"),
                    between=("Deadbush Johnston-Euphorial Airport Terminal 2", None),
                    forward_label="northbound",
                    backward_label="southbound",
                )
            elif line_name == "R23":
                RailLineBuilder(self, r_line).connect(
                    *r_stations,
                    exclude=[
                        "Sansvikk Kamprad Airfield",
                        "Sansvikk Karlstad",
                        "Sansvikk IKEA",
                    ],
                    forward_label="eastbound",
                    backward_label="westbound",
                )
                RailLineBuilder(self, r_line).connect(
                    get_stn(r_stations, "Glacierton"),
                    get_stn(r_stations, "Sansvikk Kamprad Airfield"),
                    forward_label="to Sansvikk IKEA",
                    backward_label="westbound",
                )
                RailLineBuilder(self, r_line).connect(
                    get_stn(r_stations, "Port Dupont"),
                    get_stn(r_stations, "Sansvikk Kamprad Airfield"),
                    forward_label="to Sansvikk IKEA",
                    backward_label="eastbound",
                )
                RailLineBuilder(self, r_line).connect(
                    *r_stations,
                    between=("Sansvikk Kamprad Airfield", "Sansvikk IKEA"),
                    forward_label="to Sansvikk IKEA",
                    backward_label="to mainline",
                )
            elif line_name == "R2":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Totem Beach Transit Center"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Paralia", None))
            elif line_name == "R4":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Birmingham"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Oceanside Bayfront", None))
            elif line_name == "R5":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Xterium North"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Weston East", None))
            elif line_name == "R13":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "New Foresne Cinnameadow"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Lilygrove Union", None))
            elif line_name == "R17":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Dewford City Lometa"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Fort Torbay", None))
            elif line_name == "R25":
                RailLineBuilder(self, r_line).connect(*r_stations, between=(None, "Norwrick"))
                RailLineBuilder(self, r_line).connect(*r_stations, between=("Paralia", None))
            else:
                RailLineBuilder(self, r_line).connect(*r_stations)

            if w:
                line_name = "W" + line_name[1:] if line_name.startswith("R") else line_name + " Rapid"  # noqa: PLW2901
                w_line = RailLine.new(
                    self,
                    code=line_name,
                    name=line_name,
                    company=company,
                    mode="warp",
                    colour=line_colour,
                )

                if line_name == "W2":
                    RailLineBuilder(self, w_line).connect(*w_stations, between=(None, "Totem Beach Transit Center"))
                    RailLineBuilder(self, w_line).connect(*w_stations, between=("Southbank", None))
                elif line_name == "W5":
                    RailLineBuilder(self, w_line).connect(*w_stations, between=(None, "Xterium North"))
                    RailLineBuilder(self, w_line).connect(*w_stations, between=("Weston East", None))
                else:
                    RailLineBuilder(self, w_line).connect(*w_stations)
