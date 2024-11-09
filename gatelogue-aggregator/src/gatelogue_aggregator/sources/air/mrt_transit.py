import pandas as pd

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.logging import INFO3, track
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.air import AirAirline, AirAirport, AirSource, AirFlight, AirSource, AirGate
from gatelogue_aggregator.types.source import Source


class MRTTransit(AirSource):
    name = "MRT Transit (Air)"
    priority = 2

    def __init__(self, config: Config):
        cache1 = config.cache_dir / "mrt-transit1"
        cache2 = config.cache_dir / "mrt-transit2"
        AirSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=379342597",
            cache1,
            timeout=config.timeout,
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

        df1["Raiko Airlines"] = [
            (", ".join("S" + b.strip() for b in str(a).split(",")) if str(a) != "nan" else "nan")
            for a in df1["Raiko Airlines"]
        ]

        get_url(
            "https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=248317803",
            cache2,
            timeout=config.timeout,
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

        df = pd.concat((df1, df2))

        for airline_name in track(df.columns, description=INFO3 + "Extracting data from CSV", nonlinear=True):
            if airline_name in ("Name", "Code", "World", "Operator", "Seaplane"):
                continue
            airline = AirAirline.new(self, name=AirAirline.process_airline_name(airline_name))
            for airport_name, airport_code, airport_world, flights in zip(
                df["Name"], df["Code"], df["World"], df[airline_name], strict=False
            ):
                if airport_code == "" or str(flights) == "nan":
                    continue
                airport = AirAirport.new(self, code=AirAirport.process_code(airport_code))

                if airport_name != "":
                    airport.attrs(self).name = airport_name
                if airport_world != "":
                    airport.attrs(self).world = airport_world

                gate = AirGate.new(self, code=None, airport=airport)

                for flight_code in str(flights).split(", "):
                    flight = AirFlight.new(
                        self, codes=AirFlight.process_code(flight_code, airline_name), airline=airline
                    )
                    flight.connect_one(self, airline)
                    flight.connect(self, gate)

        self.save_to_cache(config, self.g)
