from pathlib import Path

import pandas as pd
import rich.progress
import rich.status

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.types.air import AirContext, AirSource
from gatelogue_aggregator.types.base import Source, process_airport_code, process_code


class MRTTransit(AirSource):
    name = "MRT Transit"
    priority = 2

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        cache1 = cache_dir / "mrt-transit1"
        cache2 = cache_dir / "mrt-transit2"
        AirContext.__init__(self)
        Source.__init__(self)

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=379342597",
            cache1,
            timeout=timeout,
        )
        df1 = pd.read_csv(cache1, header=1)

        df1.rename(
            columns={
                "Unnamed: 0": "Name",
                "Unnamed: 1": "Code",
                "Unnamed: 2": "Operator",
            },
            inplace=True,
        )
        df1.drop(df1.tail(66).index, inplace=True)
        df1["World"] = "New"

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=248317803",
            cache2,
            timeout=timeout,
        )
        df2 = pd.read_csv(cache2, header=1)

        df2.rename(
            columns={
                "Unnamed: 0": "Name",
                "Unnamed: 1": "Code",
                "Unnamed: 2": "World",
                "Unnamed: 3": "Operator",
            },
            inplace=True,
        )
        df2.drop(df2.tail(6).index, inplace=True)

        df = pd.concat((df2, df1))

        for airline_name in rich.progress.track(df.columns[4:], "  Extracting data from CSV...", transient=True):
            airline = self.airline(name=airline_name)
            for airport_name, airport_code, airport_world, flights in zip(
                df["Name"], df["Code"], df["World"], df[airline_name], strict=False
            ):
                if airport_code == "" or str(flights) == "nan":
                    continue
                airport = self.airport(code=process_airport_code(airport_code))

                if airport_name != "":
                    airport.attrs(self).name = airport_name
                if airport_world != "":
                    airport.attrs(self).world = airport_world

                gate = self.gate(code=None, airport=airport)

                for flight_code in str(flights).split(", "):
                    flight = self.flight(codes={process_code(flight_code)}, airline=airline)
                    flight.connect_one(self, airline)
                    flight.connect(self, gate)
        rich.print("[green]  Extracted")
