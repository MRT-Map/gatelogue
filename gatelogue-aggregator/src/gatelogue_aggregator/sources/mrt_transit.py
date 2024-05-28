from gatelogue_aggregator.types.context import AirContext
import pandas as pd

from gatelogue_aggregator.types.air import Airline, Airport, Gate, Flight
from gatelogue_aggregator.types.base import Sourced


class MRTTransit(AirContext):
    def __init__(self):
        super().__init__()
        df = pd.read_csv("https://docs.google.com/spreadsheets/d/1wzvmXHQZ7ee7roIvIrJhkP6oCegnB8-nefWpd8ckqps/export?format=csv&gid=248317803", header=1)
        df.rename(columns={
            'Unnamed: 0': 'Airport Name',
            'Unnamed: 1': 'Code',
            'Unnamed: 2': 'World',
            'Unnamed: 3': 'Operator',
        }, inplace=True)
        df.drop(df.tail(6).index, inplace=True)

        for airline_name in df.columns[4:]:
            airline = Sourced(self.get_airline(name=airline_name))
            for airport_code, flights in zip(df['Code'], df[airline_name]):
                if airport_code == "" or str(flights) == "nan":
                    continue
                airport = Sourced(self.get_airport(code=airport_code))
                gate = Sourced(self.get_gate(code=None, airport=airport))
                for flight_code in str(flights).split(", "):
                    flight = self.get_flight(codes=[flight_code], airline=airline)
                    flight.airline = airline
                    flight.gates.append(gate)

        self.update()
        print({a.name: len(a.flights) for a in self.airline})



