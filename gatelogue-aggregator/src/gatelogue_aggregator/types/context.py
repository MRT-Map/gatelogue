from typing import Generator

import msgspec

from gatelogue_aggregator.types.air import Flight, Airport, Gate, Airline
from gatelogue_aggregator.types.base import Sourced


class AirContext:
    flight: list[Flight]
    airport: list[Airport]
    gate: list[Gate]
    airline: list[Airline]

    def __init__(self):
        self.flight = []
        self.airport = []
        self.gate = []
        self.airline = []

    def get_flight(self, **query) -> Flight:
        for o in self.flight:
            if all(v == getattr(o, k) for k, v in query.items()):
                return o
        o = Flight(**query)
        o.ctx(self)
        return o

    def get_airport(self, **query) -> Airport:
        for o in self.airport:
            if all(v == getattr(o, k) for k, v in query.items()):
                return o
        o = Airport(**query)
        o.ctx(self)
        return o

    def get_gate(self, **query) -> Gate:
        for o in self.gate:
            if all(v == getattr(o, k) for k, v in query.items()):
                return o
        o = Gate(**query)
        o.ctx(self)
        return o

    def get_airline(self, **query) -> Airline:
        for o in self.airline:
            if all(v == getattr(o, k) for k, v in query.items()):
                return o
        o = Airline(**query)
        o.ctx(self)
        return o

    def update(self):
        for o in self.flight:
            o.update()
        for o in self.airport:
            o.update()
        for o in self.gate:
            o.update()
        for o in self.airline:
            o.update()

class Context(AirContext):
    pass
