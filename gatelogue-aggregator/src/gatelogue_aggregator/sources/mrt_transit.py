from pathlib import Path

import pandas as pd
import rich.progress
import rich.status

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url
from gatelogue_aggregator.types.air import AirContext
from gatelogue_aggregator.types.base import Source


class MRTTransit(AirContext, Source):
    name = "MRT Transit"

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT):
        cache = cache_dir / "mrt-transit"
        AirContext.__init__(self)
        Source.__init__(self)

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=248317803",
            cache,
            timeout=timeout,
        )
        df = pd.read_csv(cache, header=1)

        df.rename(
            columns={
                "Unnamed: 0": "Airport Name",
                "Unnamed: 1": "Code",
                "Unnamed: 2": "World",
                "Unnamed: 3": "Operator",
            },
            inplace=True,
        )
        df.drop(df.tail(6).index, inplace=True)

        for airline_name in rich.progress.track(df.columns[4:], "  Extracting data from CSV...", transient=True):
            airline = self.get_airline(name=airline_name).source(self)
            for airport_code, flights in zip(df["Code"], df[airline_name]):
                if airport_code == "" or str(flights) == "nan":
                    continue
                airport = self.get_airport(code=airport_code).source(self)
                gate = self.get_gate(code=None, airport=airport).source(self)
                for flight_code in str(flights).split(", "):
                    flight = self.get_flight(codes={flight_code}, airline=airline)
                    flight.airline = airline
                    flight.gates.append(gate)
        rich.print("[green]  Extracted")

        self.update()
