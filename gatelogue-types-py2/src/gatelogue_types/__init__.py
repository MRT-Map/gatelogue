from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Self, LiteralString, Iterator, Iterable, Literal



class GD:
    def __init__(self):
        sqlite3.threadsafety = 3
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = true")

    @classmethod
    def create(cls, sources: list[str]) -> Self:
        self = cls()
        cur = self.conn.cursor()
        with open(Path(__file__).parent / "create.sql") as f:
            cur.executescript(f.read())
        cur.executemany("INSERT INTO Source VALUES (?, ?)", list(enumerate(sources)))
        self.conn.commit()
        return self


class _Column[T]:
    def __init__(self, name: LiteralString, table: LiteralString, sourced: bool = False):
        self.name = name
        self.table = table
        self.sourced = sourced

    def __get__(self, instance: Node, owner: type[Node]) -> T:
        cur = instance.conn.cursor()
        return cur.execute(f"SELECT {self.name} FROM {self.table} WHERE i = :i", dict(i=instance.i)).fetchone()[0]

    def __set__(self, instance: Node, value: T):
        cur = instance.conn.cursor()
        cur.execute(f"UPDATE {self.table} SET {self.name} = :value WHERE i = :i", dict(value=value, i=instance.i))
        if self.sourced:
            cur.execute(
                f"UPDATE {self.table + 'Sourced'} SET {self.name} = :bool WHERE i = :i AND source = :source",
                dict(bool=value is not None, i=instance.i, source=instance.source),
            )


class _FKColumn[T: Node | None]:
    def __init__(self, ty: type[T], name: LiteralString, table: LiteralString, sourced: bool = False):
        self.name = name
        self.table = table
        self.sourced = sourced
        self.ty = ty

    def __get__(self, instance: Node, owner: type[Node]) -> T:
        target_i = _Column(self.name, self.table, self.sourced).__get__(instance, owner)
        if target_i is None:
            return None
        return self.ty(instance.conn, target_i)

    def __set__(self, instance: Node, value: T):
        _Column(self.name, self.table, self.sourced).__set__(instance, None if value is None else value.i)


class _SetAttr[T]:
    def __init__(self, table: LiteralString, table_column: LiteralString):
        self.table = table
        self.table_column = table_column

    def __get__(self, instance: Node, owner: type[Node]) -> set[T]:
        cur = instance.conn.cursor()
        return {
            v
            for (v,) in cur.execute(
                f"SELECT {self.table_column} FROM {self.table} WHERE i = :i", dict(i=instance.i)
            ).fetchall()
        }


class Node:
    def __init__(self, conn: sqlite3.Connection, i: int):
        self.conn = conn
        self.i = i

    type = _Column[str]("type", "Node")
    source = _Column[int]("source", "NodeSource")

    @classmethod
    def create_node(cls, conn: sqlite3.Connection, src: int, *, ty: str) -> int:
        cur = conn.cursor()
        cur.execute("INSERT INTO Node ( type ) VALUES ( :type )", dict(type=ty))
        (i,) = cur.execute("SELECT i FROM Node WHERE ROWID = :rowid", dict(rowid=cur.lastrowid)).fetchone()
        cur.execute("INSERT INTO NodeSource ( i, source ) VALUES ( :i, :source )", dict(i=i, source=src))
        return i


class LocatedNode(Node):
    world = _Column[str | None]("world", "LocatedNode")
    _x = _Column[int | None]("x", "LocatedNode")
    _y = _Column[int | None]("y", "LocatedNode")

    @property
    def coordinates(self) -> tuple[int, int] | None:
        if (x := self._x) is None:
            return None
        if (y := self._y) is None:
            return None
        return x, y

    @coordinates.setter
    def coordinates(self, value: tuple[int, int] | None):
        x, y = (None, None) if value is None else value
        self._x = x
        self._y = y

    @classmethod
    def create_node_with_location(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        ty: str,
        world: str | None = None,
        coordinates: tuple[int, int] | None = None,
    ) -> int:
        i = cls.create_node(conn, src, ty=ty)
        x, y = (None, None) if coordinates is None else coordinates
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO NodeLocation (i, world, x, y) VALUES (:i, :world, :x, :y)",
            dict(i=i, world=world, x=x, y=y),
        )
        cur.execute(
            "INSERT INTO NodeLocationSource (i, source, world, coordinates) VALUES (:i, :source, :world, :coordinates)",
            dict(i=i, source=src, world=world is not None, coordinates=coordinates is not None),
        )
        return i


class AirAirline(Node):
    name = _Column[str]("name", "AirAirline")
    link = _Column[str | None]("link", "AirAirline", sourced=True)

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, *, name: str, link: str | None = None) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO AirAirline (i, name, link) VALUES (:i, :name, :link)", dict(i=i, name=name, link=link))
        cur.execute(
            "INSERT INTO AirAirlineSource (i, source, link) VALUES (:i, :source, :link)",
            dict(i=i, source=src, link=link is not None),
        )
        return cls(conn, i)

    @property
    def flights(self) -> Iterator[AirFlight]:
        return (
            AirFlight(self.conn, i)
            for i in self.conn.execute("SELECT i FROM AirFlight WHERE airline = :i", dict(i=self.i)).fetchall()
        )

    @property
    def gates(self) -> Iterator[AirGate]:
        return (
            AirGate(self.conn, i)
            for i in self.conn.execute("SELECT i FROM AirGate WHERE airline = :i", dict(i=self.i)).fetchall()
        )

    @property
    def airports(self) -> Iterator[AirAirport]:
        return (
            AirAirport(self.conn, i)
            for i in self.conn.execute(
                "SELECT DISTINCT AirAirport.i "
                "FROM AirGate LEFT JOIN AirAirport on AirAirport.i = AirGate.airport "
                "WHERE AirGate.airline = :i",
                dict(i=self.i),
            ).fetchall()
        )


class AirAirport(LocatedNode):
    code = _Column[str]("code", "AirAirport")
    names = _SetAttr[str]("AirAirportNames", "name")
    link = _Column[str | None]("link", "AirAirport", sourced=True)
    modes = _SetAttr[str]("AirAirportModes", "mode")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        code: str,
        names: set[str] | None = None,
        link: str | None = None,
        modes: set[str] | None = None,
        world: str | None = None,
        coordinates: tuple[int, int] | None = None,
    ) -> Self:
        if names is None:
            names = set()
        if modes is None:
            modes = set()
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, world=world, coordinates=coordinates)
        cur = conn.cursor()
        cur.execute("INSERT INTO AirAirport (i, code, link) VALUES (:i, :code, :link)", dict(i=i, code=code, link=link))
        cur.executemany("INSERT INTO AirAirportNames (i, name) VALUES (?, ?)", [(i, name) for name in names])
        cur.executemany("INSERT INTO AirAirportModes (i, mode) VALUES (?, ?)", [(i, mode) for mode in modes])
        cur.execute(
            "INSERT INTO AirAirportSource (i, source, names, link, modes) VALUES (:i, :source, :names, :link, :modes)",
            dict(i=i, source=src, names=len(names) > 0, link=link is not None, modes=len(modes) > 0),
        )
        return cls(conn, i)

    @property
    def gates(self) -> Iterator[AirGate]:
        return (
            AirGate(self.conn, i)
            for i in self.conn.execute("SELECT i FROM AirGate WHERE airport = :i", dict(i=self.i)).fetchall()
        )


class AirGate(Node):
    code = _Column[str | None]("code", "AirGate")
    airport = _FKColumn(AirAirport, "airport", "AirGate")
    airline = _FKColumn[AirAirline | None](AirAirline, "airline", "AirGate")
    size = _Column[str | None]("size", "AirGate")
    mode = _Column[str | None]("mode", "AirGate")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        code: str | None,
        airport: AirAirport,
        airline: AirAirline | None = None,
        size: str | None = None,
        mode: str | None = None,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO AirGate (i, code, airport, airline, size, mode) VALUES (:i, :code, :airport, :airline, :size, :mode)",
            dict(
                i=i, code=code, airport=airport.i, airline=None if airline is None else airline.i, size=size, mode=mode
            ),
        )
        cur.execute(
            "INSERT INTO AirGateSource (i, source, size, mode, airline) VALUES (:i, :source, :size, :mode, :airline)",
            dict(i=i, source=src, size=size is not None, mode=mode is not None, airline=airline is not None),
        )
        return cls(conn, i)

    @property
    def flights_from_here(self) -> Iterator[AirFlight]:
        return (
            AirFlight(self.conn, i)
            for i in self.conn.execute('SELECT i FROM AirFlight WHERE "from" = :i', dict(i=self.i)).fetchall()
        )

    @property
    def flights_to_here(self) -> Iterator[AirFlight]:
        return (
            AirFlight(self.conn, i)
            for i in self.conn.execute('SELECT i FROM AirFlight WHERE "to" = :i', dict(i=self.i)).fetchall()
        )


class AirFlight(Node):
    airline = _FKColumn(AirAirline, "airline", "AirFlight")
    code = _Column[str]("code", "AirFlight")
    from_ = _FKColumn(AirGate, "from", "AirFlight")
    to = _FKColumn(AirGate, "to", "AirFlight")
    mode = _Column[str | None]("mode", "AirFlight")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        airline: AirAirline,
        code: str,
        from_: AirGate,
        to: AirGate,
        mode: str | None = None,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO AirFlight (i, "from", "to", code, mode, airline) VALUES (:i, :from_, :to, :code, :mode, :airline)',
            dict(i=i, from_=from_.i, to=to.i, code=code, mode=mode, airline=airline.i),
        )
        cur.execute(
            "INSERT INTO AirFlightSource (i, source, mode) VALUES (:i, :source, :mode)",
            dict(
                i=i,
                source=src,
                mode=mode is not None,
            ),
        )
        return cls(conn, i)


if __name__ == "__main__":
    gd = GD.create(["Temp"])
    airline = AirAirline.create(gd.conn, 0, name="a")
    airport = AirAirport.create(gd.conn, 0, code="AAA")
    gate = AirGate.create(gd.conn, 0, airport=airport, code="A")
    flight = AirFlight.create(gd.conn, 0, airline=airline, code="B", from_=gate, to=gate)
