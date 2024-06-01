from pathlib import Path

import pandas as pd
import rich.progress
import rich.status

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.types.air import AirContext
from gatelogue_aggregator.types.base import Source, Sourced, process_code, process_airport_code


class MRTTransit(AirContext, Source):
    name = "MRT Transit"

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        cache1 = cache_dir / "mrt-transit1"
        cache2 = cache_dir / "mrt-transit2"
        AirContext.__init__(self)
        Source.__init__(self)

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=248317803",
            cache1,
            timeout=timeout,
        ).encode("latin").decode("utf-8")
        df = pd.read_csv(cache1, header=1)

        df.rename(
            columns={
                "Unnamed: 0": "Name",
                "Unnamed: 1": "Code",
                "Unnamed: 2": "World",
                "Unnamed: 3": "Operator",
            },
            inplace=True,
        )
        df.drop(df.tail(6).index, inplace=True)

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=379342597",
            cache2,
            timeout=timeout,
        ).encode("latin").decode("utf-8")
        df2 = pd.read_csv(cache2, header=1)

        df2.rename(
            columns={
                "Unnamed: 0": "Name",
                "Unnamed: 1": "Code",
                "Unnamed: 2": "Operator",
            },
            inplace=True,
        )
        df2.drop(df2.tail(66).index, inplace=True)
        df2["World"] = "New"
        df = pd.concat((df, df2))

        for airline_name in rich.progress.track(df.columns[4:], "  Extracting data from CSV...", transient=True):
            airline = self.get_airline(name=airline_name).source(self)
            for airport_name, airport_code, airport_world, flights in zip(
                df["Name"], df["Code"], df["World"], df[airline_name]
            ):
                if airport_code == "" or str(flights) == "nan":
                    continue
                airport = self.get_airport(code=process_airport_code(airport_code)).source(self)

                if airport_name != "":
                    airport.v.name = Sourced(airport_name).source(self)
                if airport_world != "":
                    airport.v.world = Sourced(airport_world).source(self)

                gate = self.get_gate(code=None, airport=airport).source(self)
                for flight_code in str(flights).split(", "):
                    flight = self.get_flight(codes={process_code(flight_code)}, airline=airline)
                    flight.airline = airline
                    flight.gates.append(gate)
        rich.print("[green]  Extracted")

        self.update()
