from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Self, LiteralString, Iterator


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
        return cur.execute(f"SELECT {self.name} FROM {self.table} WHERE i = :i", {"i": instance.i}).fetchone()[0]

    def __set__(self, instance: Node, value: T):
        cur = instance.conn.cursor()
        cur.execute(f"UPDATE {self.table} SET {self.name} = :value WHERE i = :i", {"value": value, "i": instance.i})
        if self.sourced:
            cur.execute(f"UPDATE {self.table + "Sourced"} SET {self.name} = :bool WHERE i = :i AND source = :source",
                        {"bool": value is not None, "i": instance.i, "source": instance.source})


class Node:
    def __init__(self, conn: sqlite3.Connection, i: int):
        self.conn = conn
        self.i = i

    type = _Column[str]("type", "Node")
    source = _Column[int]("source", "NodeSource")

    @classmethod
    def create_node(cls, conn: sqlite3.Connection, src: int, *, ty: str) -> int:
        cur = conn.cursor()
        cur.execute("INSERT INTO Node ( type ) VALUES ( :type )", {"type": ty})
        i, = cur.execute("SELECT i FROM Node WHERE ROWID = :rowid", {"rowid": cur.lastrowid}).fetchone()
        cur.execute("INSERT INTO NodeSource ( i, source ) VALUES ( :i, :source )", {"i": i, "source": src})
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
    def create_node_with_location(cls, conn: sqlite3.Connection, src: int, *, ty: str, world: str | None = None,
                                  coordinates: tuple[int, int] | None = None) -> int:
        i = cls.create_node(conn, src, ty=ty)
        x, y = (None, None) if coordinates is None else coordinates
        cur = conn.cursor()
        cur.execute("INSERT INTO NodeLocation (i, world, x, y) VALUES (:i, :world, :x, :y)", {
            "i": i,
            "world": world,
            "x": x, "y": y
        })
        cur.execute("INSERT INTO NodeLocationSource (i, source, world, coordinates) VALUES (:i, :source, :world, :coordinates)",
                    {
                        "i": i,
                        "source": src,
                        "world": world is not None,
                        "coordinates": coordinates is not None
                    })
        return i


class AirAirline(Node):
    name = _Column[str]("name", "AirAirline")
    link = _Column[str | None]("link", "AirAirline", sourced=True)

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, *, name: str, link: str | None = None) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO AirAirline (i, name, link) VALUES (:i, :name, :link)", {
            "i": i,
            "name": name,
            "link": link
        })
        cur.execute("INSERT INTO AirAirlineSource (i, source, link) VALUES (:i, :source, :link)", {
            "i": i,
            "source": src,
            "link": link is not None
        })
        return cls(conn, i)

    @property
    def flights(self) -> Iterator[AirFlight]:
        return (AirFlight(self.conn, i) for i in
                self.conn.execute("SELECT i FROM AirFlight WHERE airline = ?", (self.i,)).fetchall())

    @property
    def gates(self) -> Iterator[AirGate]:
        return (AirGate(self.conn, i) for i in
                self.conn.execute("SELECT i FROM AirGate WHERE airline = ?", (self.i,)).fetchall())

    @property
    def airports(self) -> Iterator[AirAirport]:
        return (AirAirport(self.conn, i) for i in self.conn.execute(
            "SELECT DISTINCT AirAirport.i "
            "FROM AirGate LEFT JOIN AirAirport on AirAirport.i = AirGate.airport "
            "WHERE AirGate.airline = ?",
            (self.i,)).fetchall())


if __name__ == "__main__":
    gd = GD.create(["Temp"])
    node = AirAirline.create(gd.conn, 0, name="a")
    print(node.name)
