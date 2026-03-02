from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Unpack

import gatelogue_types as gt
import rich

from gatelogue_aggregator.logging import ERROR, INFO1, report
from gatelogue_aggregator.sources.air import hardcode
from gatelogue_aggregator.sources.line_builder import BusLineBuilder, RailLineBuilder, SeaLineBuilder

if TYPE_CHECKING:
    import sqlite3

    from gatelogue_aggregator.config import Config


class Source:
    name: ClassVar[str]
    priority: ClassVar[int] = -1
    report_ignore: tuple[type[gt.Node], ...] = ()
    conn: sqlite3.Connection

    def __init__(self, config: Config, conn: sqlite3.Connection):
        self.conn = conn
        rich.print(INFO1 + f"Preparing raw data for {self.name}")

        self.prepare(config)

    def prepare(self, config: Config):
        pass

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
            rich.print(ERROR + f"{self.name} yielded no results")

        for node in nodes:
            report(node, prefix=self.name, ignore=self.report_ignore)


class AirSource(Source):
    def airline(self, **kwargs: Unpack[gt.AirAirline.CreateParams]) -> gt.AirAirline:
        kwargs["name"] = kwargs["name"].strip()
        kwargs["name"] = hardcode.AIRLINE_ALIASES.get(kwargs["name"], kwargs["name"])
        return gt.AirAirline.create(self.conn, self.priority, **kwargs)

    def airport(self, **kwargs: Unpack[gt.AirAirport.CreateParams]) -> gt.AirAirport:
        kwargs["code"] = kwargs["code"].strip()
        kwargs["code"] = hardcode.AIRPORT_ALIASES.get(kwargs["code"], kwargs["code"])
        return gt.AirAirport.create(self.conn, self.priority, **kwargs)

    def gate(self, **kwargs: Unpack[gt.AirGate.CreateParams]) -> gt.AirGate:
        if kwargs["code"] is not None:
            kwargs["code"] = kwargs["code"].strip()
        kwargs["code"] = (
            d.get(kwargs["code"], kwargs["code"])
            if (d := hardcode.GATE_ALIASES.get(kwargs["airport"].code)) is not None
            else kwargs["code"]
        )
        if (
            kwargs["airport"].code in hardcode.DUPLICATE_GATE_NUM
            and kwargs["code"] is not None
            and not kwargs["code"].startswith("T")
        ):
            rich.print(
                ERROR + self.name + f": Received gate code without terminal `{kwargs['airport'].code} {kwargs['code']}`"
            )
        return gt.AirGate.create(self.conn, self.priority, **kwargs)

    def flight(self, **kwargs: Unpack[gt.AirFlight.CreateParams]) -> gt.AirFlight:
        return gt.AirFlight.create(self.conn, self.priority, **kwargs)

    def connect(
        self,
        *,
        airline: gt.AirAirline,
        flight_code1: str,
        flight_code2: str | None,
        airport1_code: str = "",
        airport2_code: str = "",
        gate1_code: str | None = None,
        gate2_code: str | None = None,
        airport1_name: str | None = None,
        airport2_name: str | None = None,
        aircraft_name: str | None = None,
        mode: gt.AirMode | None = None,
    ):
        aircraft = None if aircraft_name is None else gt.Aircraft(self.conn, aircraft_name)
        mode = mode or (aircraft.mode if aircraft is not None else "warp plane")

        airport1 = self.airport(code=airport1_code, names=None if airport1_name is None else {airport1_name})
        gate1 = self.gate(code=gate1_code, airport=airport1, mode=mode, airline=airline)

        airport2 = self.airport(code=airport2_code, names=None if airport2_name is None else {airport2_name})
        gate2 = self.gate(code=gate2_code, airport=airport2, mode=mode, airline=airline)

        self.flight(airline=airline, code=flight_code1, from_=gate1, to=gate2, aircraft=aircraft_name)
        if flight_code2 is not None:
            self.flight(airline=airline, code=flight_code2, from_=gate2, to=gate1, aircraft=aircraft_name)


class BusSource(Source):
    def company(self, **kwargs: Unpack[gt.BusCompany.CreateParams]) -> gt.BusCompany:
        return gt.BusCompany.create(self.conn, self.priority, **kwargs)

    def line(self, **kwargs: Unpack[gt.BusLine.CreateParams]) -> gt.BusLine:
        return gt.BusLine.create(self.conn, self.priority, **kwargs)

    def stop(self, **kwargs: Unpack[gt.BusStop.CreateParams]) -> gt.BusStop:
        return gt.BusStop.create(self.conn, self.priority, **kwargs)

    def berth(self, **kwargs: Unpack[gt.BusBerth.CreateParams]) -> gt.BusBerth:
        return gt.BusBerth.create(self.conn, self.priority, **kwargs)

    def connection(self, **kwargs: Unpack[gt.BusConnection.CreateParams]) -> gt.BusConnection:
        return gt.BusConnection.create(self.conn, self.priority, **kwargs)

    def builder(self, line: gt.BusLine) -> BusLineBuilder:
        return BusLineBuilder(self.priority, line)


class SeaSource(Source):
    def company(self, **kwargs: Unpack[gt.SeaCompany.CreateParams]) -> gt.SeaCompany:
        return gt.SeaCompany.create(self.conn, self.priority, **kwargs)

    def line(self, **kwargs: Unpack[gt.SeaLine.CreateParams]) -> gt.SeaLine:
        return gt.SeaLine.create(self.conn, self.priority, **kwargs)

    def stop(self, **kwargs: Unpack[gt.SeaStop.CreateParams]) -> gt.SeaStop:
        return gt.SeaStop.create(self.conn, self.priority, **kwargs)

    def dock(self, **kwargs: Unpack[gt.SeaDock.CreateParams]) -> gt.SeaDock:
        return gt.SeaDock.create(self.conn, self.priority, **kwargs)

    def connection(self, **kwargs: Unpack[gt.SeaConnection.CreateParams]) -> gt.SeaConnection:
        return gt.SeaConnection.create(self.conn, self.priority, **kwargs)

    def builder(self, line: gt.SeaLine) -> SeaLineBuilder:
        return SeaLineBuilder(self.priority, line)


class RailSource(Source):
    def company(self, **kwargs: Unpack[gt.RailCompany.CreateParams]) -> gt.RailCompany:
        return gt.RailCompany.create(self.conn, self.priority, **kwargs)

    def line(self, **kwargs: Unpack[gt.RailLine.CreateParams]) -> gt.RailLine:
        return gt.RailLine.create(self.conn, self.priority, **kwargs)

    def station(self, **kwargs: Unpack[gt.RailStation.CreateParams]) -> gt.RailStation:
        return gt.RailStation.create(self.conn, self.priority, **kwargs)

    def platform(self, **kwargs: Unpack[gt.RailPlatform.CreateParams]) -> gt.RailPlatform:
        return gt.RailPlatform.create(self.conn, self.priority, **kwargs)

    def connection(self, **kwargs: Unpack[gt.RailConnection.CreateParams]) -> gt.RailConnection:
        return gt.RailConnection.create(self.conn, self.priority, **kwargs)

    def builder(self, line: gt.RailLine) -> RailLineBuilder:
        return RailLineBuilder(self.priority, line)
