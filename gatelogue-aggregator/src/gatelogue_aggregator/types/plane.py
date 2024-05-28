from __future__ import annotations

from typing import NewType

import msgspec

from gatelogue_aggregator.types.sourced import Sourced


class Flight(msgspec.Struct):
    id: FlightID
    codes: list[str]
    gates: list[Sourced[GateID]]
    airlines: list[Sourced[AirlineID]]


FlightID = NewType("FlightID", str)


class Airport(msgspec.Struct):
    id: AirportID
    code: str
    coordinates: Sourced[tuple[int, int]]
    gates: list[Sourced[GateID]]


AirportID = NewType("AirportID", str)


class Gate(msgspec.Struct):
    id: GateID
    code: str
    flights: list[Sourced[FlightID]]
    airport: Sourced[AirportID]
    size: Sourced[str]


GateID = NewType("GateID", str)


class Airline(msgspec.Struct):
    id: AirlineID
    name: str
    flights: list[Sourced[FlightID]]


AirlineID = NewType("AirlineID", str)
