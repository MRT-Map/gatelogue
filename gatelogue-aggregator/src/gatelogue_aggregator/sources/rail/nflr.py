from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.source import RailSource


class NFLR(RailSource):
    name = "MRT Wiki (Rail, nFLR)"
    cache: Path
    lines: list[tuple[str, str, bool, int]]

    def prepare(self, config: Config):
        self.cache = config.cache_dir / "nflr"
        get_url(
            "https://docs.google.com/spreadsheets/d/1ohIRZrcLZByL5feqDqgA0QeC3uwAlBKOMKxWMRTSxRw/export?format=csv&gid=1540849896",
            self.cache / "lines",
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        df = pd.read_csv(self.cache / "lines")
        self.lines = [
            (str(line_name), str(back), bool(w), int(gid))
            for line_name, back, w, gid in zip(df["line"], df["back"], df["w"], df["gid"], strict=False)
            if str(gid) != "nan"
        ]

        def retrieve_urls(line_name: str, gid: int):
            get_url(
                "https://docs.google.com/spreadsheets/d/1ohIRZrcLZByL5feqDqgA0QeC3uwAlBKOMKxWMRTSxRw/export?format=csv&gid="
                + str(gid),
                self.cache / line_name,
                timeout=config.timeout,
                cooldown=config.cooldown,
            )

        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            list(executor.map(lambda s: retrieve_urls(s[0], s[3]), self.lines))

    def build(self, config: Config):
        company = self.company(name="nFLR")

        for line_name, line_colour, w, _ in self.lines:
            df = pd.read_csv(self.cache / line_name)

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
                    station = station or self.station(codes=code, company=company, name=name)
                    r_stations.append(station)
                if "W" in route and w:
                    station = station or self.station(codes=code, company=company, name=name)
                    w_stations.append(station)

            r_line = self.line(
                code=line_name,
                name=line_name,
                company=company,
                mode="warp",
                colour=line_colour,
            )
            r_builder = self.builder(r_line)
            r_builder.add(*r_stations)

            if line_name == "R7A":
                r_builder.connect_circle(forward_direction="clockwise", backward_direction="anticlockwise")
            elif line_name == "R5A":
                r_builder.connect(
                    until="Deadbush Euphorial", forward_direction="southbound", backward_direction="northbound"
                )
                r_builder.connect(
                    until="Deadbush Quarryville", forward_direction="southbound", backward_direction="northbound CW"
                )
                r_builder.connect(
                    until="Deadbush Johnston-Euphorial Airport Terminal 2",
                    forward_direction="northbound ACW",
                    backward_direction="southbound",
                )
                r_builder.connect(forward_direction="northbound", backward_direction="southbound")
                r_builder.connect_to(
                    "Deadbush Karaj Expo", forward_direction="northbound", backward_direction="southbound"
                )
            elif line_name == "R23":
                r_builder.connect(until="Glacierton", forward_direction="eastbound", backward_direction="westbound")

                branch = r_builder.branch_off()
                branch.connect(
                    until="Sansvikk Kamprad Airfield",
                    forward_direction="towards Sansvikk IKEA",
                    backward_direction="westbound",
                )
                branch.branch_off().u_turn().connect_to(
                    "Port Dupont", forward_direction="eastbound", backward_direction="towards Sansvikk IKEA"
                )
                branch.connect(
                    until="Sansvikk IKEA",
                    forward_direction="towards Sansvikk IKEA",
                    backward_direction="towards mainline",
                )

                r_builder.connect(forward_direction="eastbound", backward_direction="westbound")
            elif line_name == "R4":
                r_builder.connect(until="Birmingham")
                r_builder.skip(until="Oceanside Bayfront", detached=True)
                r_builder.connect()
            elif line_name == "R5":
                r_builder.connect(until="Xterium North")
                r_builder.skip(until="Weston East", detached=True)
                r_builder.connect()
            elif line_name == "R13":
                r_builder.connect(until="New Foresne Cinnameadow")
                r_builder.skip(until="Lilygrove Union", detached=True)
            elif line_name == "R17":
                r_builder.connect(until="Dewford City Lometa")
                r_builder.skip(until="Fort Torbay", detached=True)
                r_builder.connect()
            elif line_name == "R25":
                r_builder.connect(until="Norwrick")
                r_builder.skip(until="Totem Beach Transit Center", detached=True)
                r_builder.connect()
            else:
                r_builder.connect()

            if w:
                line_name = "W" + line_name[1:] if line_name.startswith("R") else line_name + " Rapid"  # noqa: PLW2901
                w_line = self.line(
                    code=line_name,
                    name=line_name,
                    company=company,
                    mode="warp",
                    colour=line_colour,
                )
                w_builder = self.builder(w_line)
                w_builder.add(*w_stations)

                if line_name == "W5":
                    w_builder.connect(until="Xterium North")
                    w_builder.skip(until="Weston East", detached=True)
                    w_builder.connect()
                else:
                    w_builder.connect()
