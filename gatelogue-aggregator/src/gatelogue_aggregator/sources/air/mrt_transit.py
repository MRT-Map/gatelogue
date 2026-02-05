from __future__ import annotations

import re
from typing import TYPE_CHECKING, override

import pandas as pd

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.logging import INFO3, track
from gatelogue_aggregator.source import AirSource

if TYPE_CHECKING:
    from gatelogue_aggregator.config import Config
    import gatelogue_types as gt


class MRTTransit(AirSource):
    name = "MRT Transit (Air)"
    df: pd.DataFrame

    def prepare(self, config: Config):
        cache1 = config.cache_dir / "mrt-transit1"
        cache2 = config.cache_dir / "mrt-transit2"
        cache3 = config.cache_dir / "mrt-transit3"

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=379342597",
            cache1,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        df1 = pd.read_csv(cache1, header=1)

        df1.rename(
            columns={
                "Unnamed: 0": "Name",
                "Unnamed: 1": "Code",
                "Unnamed: 2": "World",
                "Unnamed: 3": "Operator",
            },
            inplace=True,
        )
        df1.drop(df1.tail(66).index, inplace=True)
        df1["Mode"] = "seaplane"

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=1714326420",
            cache2,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        df2 = pd.read_csv(cache2, header=0)
        df2["Mode"] = "helicopter"
        df2.rename(columns={"Airport Name": "Name"}, inplace=True)
        df2.drop(df2.tail(4).index, inplace=True)

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=248317803",
            cache3,
            timeout=config.timeout,
            cooldown=config.cooldown,
        )
        df3 = pd.read_csv(cache3, header=1)
        df3["Mode"] = "warp plane"

        df3.rename(
            columns={
                "Unnamed: 0": "Name",
                "Unnamed: 1": "Code",
                "Unnamed: 2": "World",
                "Unnamed: 3": "Operator",
            },
            inplace=True,
        )
        df3.drop(df3.tail(6).index, inplace=True)

        self.df = pd.concat((df1, df2, df3))

    def build(self, config: Config):
        for airline_name in track(self.df.columns, INFO3, description="Extracting data from CSV", nonlinear=True):
            if airline_name in ("Name", "Code", "World", "Operator", "Owner", "Mode"):
                continue
            airline = self.airline(name=airline_name)
            code2dest: dict[str, list[gt.AirAirport]] = {}

            for airport_name, airport_code, airport_world, mode, flights in zip(
                self.df["Name"], self.df["Code"], self.df["World"], self.df["Mode"], self.df[airline_name], strict=False
            ):
                if airport_code == "" or str(flights) == "nan":
                    continue
                airport = self.airport(code=airport_code, modes={mode})

                if str(airport_name) != "nan":
                    if "(" in airport_name:
                        matches = re.search(r"(.*?) \((.*?)\)", str(airport_name))
                        names = {matches.group(2) + " " + matches.group(1), airport_name}
                    else:
                        names = {airport_name}
                    if airport_code == "CWI":
                        names.update({"UCWT International Airport", "UCWTIA"})
                    airport.names = names
                if str(airport_world) != "nan":
                    airport.world = airport_world

                if mode == "helicopter":
                    continue

                for flight_code in str(flights).split(", "):
                    gate = self.gate(
                        code=None,
                        airport=airport,
                        mode=mode,
                    )
                    for other_airport in code2dest.setdefault(flight_code, []):
                        other_gate = self.gate(
                            code=None,
                            airport=other_airport,
                            mode=mode,
                        )
                        self.flight(airline=airline, code=flight_code, from_=gate, to=other_gate, mode=mode)
                        self.flight(airline=airline, code=flight_code, from_=other_gate, to=gate, mode=mode)
                    code2dest[flight_code].append(airport)