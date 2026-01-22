from __future__ import annotations

import pickle
import sqlite3
from typing import TYPE_CHECKING, ClassVar, Generic, Self, TypeVar, Unpack

import gatelogue_types as gt
import rich

from gatelogue_aggregator.logging import ERROR, INFO1
from gatelogue_aggregator.sources import SOURCES
from gatelogue_types import node, air, bus, sea, rail

if TYPE_CHECKING:
    from gatelogue_aggregator.types.config import Config


class Source:
    name: ClassVar[str]
    priority: ClassVar[int] = -1
    conn: sqlite3.Connection

    def __init__(self, config: Config, conn: sqlite3.Connection):
        self.conn = conn
        rich.print(INFO1 + f"Retrieving from {self.name}")

        self.build(config)
        self.report()

    def build(self, config: Config):
        raise NotImplementedError

    def report(self):
        nodes = [
            gt.Node.auto_type(self.conn, i)
            for i, ty in self.conn.execute(
                "SELECT Node.i, type FROM NodeSource LEFT JOIN Node on Node.i = NodeSource.i WHERE source = :priority",
                dict(priority=self.priority),
            ).fetchall()
        ]

        if len(nodes) == 0:
            rich.print(ERROR + f"{self.__name__} yielded no results")

        for node in nodes:
            node.report(self)


class AirSource(Source):
    def airline(self, **kwargs: Unpack[air.AirAirline.CreateParams]) -> air.AirAirline:
        return air.AirAirline.create(self.conn, self.priority, **kwargs)

    def airport(self, **kwargs: Unpack[air.AirAirport.CreateParams]) -> air.AirAirport:
        return air.AirAirport.create(self.conn, self.priority, **kwargs)

    def gate(self, **kwargs: Unpack[air.AirGate.CreateParams]) -> air.AirGate:
        return air.AirGate.create(self.conn, self.priority, **kwargs)

    def flight(self, **kwargs: Unpack[air.AirFlight.CreateParams]) -> air.AirFlight:
        return air.AirFlight.create(self.conn, self.priority, **kwargs)


class BusSource(Source):
    def company(self, **kwargs: Unpack[bus.BusCompany.CreateParams]) -> bus.BusCompany:
        return bus.BusCompany.create(self.conn, self.priority, **kwargs)

    def line(self, **kwargs: Unpack[bus.BusLine.CreateParams]) -> bus.BusLine:
        return bus.BusLine.create(self.conn, self.priority, **kwargs)

    def stop(self, **kwargs: Unpack[bus.BusStop.CreateParams]) -> bus.BusStop:
        return bus.BusStop.create(self.conn, self.priority, **kwargs)

    def berth(self, **kwargs: Unpack[bus.BusBerth.CreateParams]) -> bus.BusBerth:
        return bus.BusBerth.create(self.conn, self.priority, **kwargs)

    def connection(self, **kwargs: Unpack[bus.BusConnection.CreateParams]) -> bus.BusConnection:
        return bus.BusConnection.create(self.conn, self.priority, **kwargs)


class SeaSource(Source):
    def company(self, **kwargs: Unpack[sea.SeaCompany.CreateParams]) -> sea.SeaCompany:
        return sea.SeaCompany.create(self.conn, self.priority, **kwargs)

    def line(self, **kwargs: Unpack[sea.SeaLine.CreateParams]) -> sea.SeaLine:
        return sea.SeaLine.create(self.conn, self.priority, **kwargs)

    def stop(self, **kwargs: Unpack[sea.SeaStop.CreateParams]) -> sea.SeaStop:
        return sea.SeaStop.create(self.conn, self.priority, **kwargs)

    def berth(self, **kwargs: Unpack[sea.SeaDock.CreateParams]) -> sea.SeaDock:
        return sea.SeaDock.create(self.conn, self.priority, **kwargs)

    def connection(self, **kwargs: Unpack[sea.SeaConnection.CreateParams]) -> sea.SeaConnection:
        return sea.SeaConnection.create(self.conn, self.priority, **kwargs)


class RailSource(Source):
    def company(self, **kwargs: Unpack[rail.RailCompany.CreateParams]) -> rail.RailCompany:
        return rail.RailCompany.create(self.conn, self.priority, **kwargs)

    def line(self, **kwargs: Unpack[rail.RailLine.CreateParams]) -> rail.RailLine:
        return rail.RailLine.create(self.conn, self.priority, **kwargs)

    def station(self, **kwargs: Unpack[rail.RailStation.CreateParams]) -> rail.RailStation:
        return rail.RailStation.create(self.conn, self.priority, **kwargs)

    def platform(self, **kwargs: Unpack[rail.RailPlatform.CreateParams]) -> rail.RailPlatform:
        return rail.RailPlatform.create(self.conn, self.priority, **kwargs)

    def connection(self, **kwargs: Unpack[rail.RailConnection.CreateParams]) -> rail.RailConnection:
        return rail.RailConnection.create(self.conn, self.priority, **kwargs)
