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
            for (i,) in self.conn.execute("SELECT i FROM AirFlight WHERE airline = :i", dict(i=self.i)).fetchall()
        )

    @property
    def gates(self) -> Iterator[AirGate]:
        return (
            AirGate(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM AirGate WHERE airline = :i", dict(i=self.i)).fetchall()
        )

    @property
    def airports(self) -> Iterator[AirAirport]:
        return (
            AirAirport(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT airport FROM AirGate WHERE airline = :i",
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
            for (i,) in self.conn.execute("SELECT i FROM AirGate WHERE airport = :i", dict(i=self.i)).fetchall()
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
            for (i,) in self.conn.execute('SELECT i FROM AirFlight WHERE "from" = :i', dict(i=self.i)).fetchall()
        )

    @property
    def flights_to_here(self) -> Iterator[AirFlight]:
        return (
            AirFlight(self.conn, i)
            for (i,) in self.conn.execute('SELECT i FROM AirFlight WHERE "to" = :i', dict(i=self.i)).fetchall()
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


class BusCompany(Node):
    name = _Column[str]("name", "BusCompany")

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, *, name: str) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO BusCompany (i, name) VALUES (:i, :name)", dict(i=i, name=name))
        cur.execute("INSERT INTO BusCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def lines(self) -> Iterator[BusLine]:
        return (
            BusLine(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM BusLine WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def stops(self) -> Iterator[BusStop]:
        return (
            BusStop(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM BusStop WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def berths(self) -> Iterator[BusBerth]:
        return (
            BusBerth(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusBerth.i "
                "FROM (SELECT i FROM BusStop WHERE company = :i) A "
                "LEFT JOIN BusBerth on A.i = BusBerth.stop",
                dict(i=self.i),
            ).fetchall()
        )


class BusLine(Node):
    code = _Column[str]("code", "BusLine")
    company = _FKColumn(BusCompany, "company", "BusLine")
    name = _Column[str | None]("name", "BusLine", sourced=True)
    colour = _Column[str | None]("colour", "BusLine", sourced=True)
    mode = _Column[str | None]("mode", "BusLine", sourced=True)
    local = _Column[bool | None]("name", "BusLine", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        code: str,
        company: BusCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: str | None = None,
        local: bool | None = None,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO BusLine (i, code, company, name, colour, mode, local) "
            "VALUES (:i, :code, :company, :name, :colour, :mode, :local)",
            dict(i=i, code=code, company=company.i, name=name, colour=colour, mode=mode, local=local),
        )
        cur.execute(
            "INSERT INTO BusLineSource (i, source, name, colour, mode, local) "
            "VALUES (:i, :source, :name, :colour, :mode, :local)",
            dict(
                i=i,
                source=src,
                name=name is not None,
                colour=colour is not None,
                mode=mode is not None,
                local=local is not None,
            ),
        )
        return cls(conn, i)

    @property
    def berths(self) -> Iterator[BusBerth]:
        return (
            BusBerth(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusBerth.i "
                'FROM (SELECT "from", "to" FROM BusConnection WHERE line = :i) A '
                'LEFT JOIN BusBerth ON A."from" = BusBerth.i OR A."to" = BusBerth.i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def stops(self) -> Iterator[BusStop]:
        return (
            BusStop(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusBerth.stop "
                'FROM (SELECT "from", "to" FROM BusConnection WHERE line = :i) A '
                'LEFT JOIN BusBerth ON A."from" = BusBerth.i OR A."to" = BusBerth.i',
                dict(i=self.i),
            ).fetchall()
        )


class BusStop(LocatedNode):
    codes = _SetAttr[str]("BusStopCodes", "codes")
    company = _FKColumn(BusCompany, "company", "BusStop")
    name = _Column[str | None]("name", "BusStop", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        codes: set[str],
        company: BusCompany,
        name: str | None = None,
        world: str | None = None,
        coordinates: tuple[int, int] | None = None,
    ) -> Self:
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, world=world, coordinates=coordinates)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO BusStop (i, name, company) VALUES (:i, :name, :company)",
            dict(i=i, name=name, company=company.i),
        )
        cur.executemany("INSERT INTO BusStopCodes (i, code) VALUES (?, ?)", [(i, code) for code in codes])
        cur.execute(
            "INSERT INTO BusStopSource (i, source, name) VALUES (:i, :source, :name)",
            dict(i=i, source=src, name=name is not None),
        )
        return cls(conn, i)

    @property
    def berths(self) -> Iterator[BusBerth]:
        return (
            BusBerth(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM BusBerth WHERE stop = :i",
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_from_here(self) -> Iterator[BusConnection]:
        return (
            BusConnection(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusConnection.i "
                "FROM (SELECT i FROM BusBerth WHERE stop = :i) A "
                'LEFT JOIN BusConnection ON A.i = BusConnection."from"',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[BusConnection]:
        return (
            BusConnection(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusConnection.i "
                "FROM (SELECT i FROM BusBerth WHERE stop = :i) A "
                'LEFT JOIN BusConnection ON A.i = BusConnection."to"',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[BusLine]:
        return (
            BusLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusConnection.line "
                "FROM (SELECT i FROM BusBerth WHERE stop = :i) A "
                'LEFT JOIN BusConnection ON A.i = BusConnection."from" OR A.i = BusConnection."to"',
                dict(i=self.i),
            ).fetchall()
        )


class BusBerth(Node):
    code = _Column[str | None]("code", "BusBerth")
    stop = _FKColumn(BusStop, "stop", "BusStop")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        code: str | None,
        stop: BusStop,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO BusBerth (i, code, stop) VALUES (:i, :code, :stop)", dict(i=i, code=code, stop=stop.i))
        cur.execute("INSERT INTO BusBerthSource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def connections_from_here(self) -> Iterator[BusConnection]:
        return (
            BusConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT BusConnection.i FROM BusConnection WHERE BusConnection."from" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[BusConnection]:
        return (
            BusConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT BusConnection.i FROM BusConnection WHERE BusConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[BusLine]:
        return (
            BusLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusConnection.line FROM BusConnection "
                'WHERE BusConnection."from" = :i OR BusConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )


class BusConnection(Node):
    line = _FKColumn(BusLine, "line", "BusConnection")
    from_ = _FKColumn(BusBerth, "from", "BusConnection")
    to = _FKColumn(BusBerth, "to", "BusConnection")
    direction = _Column[str | None]("direction", "BusConnection", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        line: BusLine,
        from_: BusBerth,
        to: BusBerth,
        direction: str | None = None,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO BusConnection (i, line, "from", "to", direction) VALUES (:i, :line, :from_, :to, :direction)',
            dict(i=i, line=line.i, from_=from_.i, to=to.i, direction=direction),
        )
        cur.execute(
            "INSERT INTO BusConnectionSource (i, source, direction) VALUES (:i, :source, :direction)",
            dict(i=i, source=src, direction=direction is not None),
        )
        return cls(conn, i)


class SeaCompany(Node):
    name = _Column[str]("name", "SeaCompany")

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, *, name: str) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO SeaCompany (i, name) VALUES (:i, :name)", dict(i=i, name=name))
        cur.execute("INSERT INTO SeaCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def lines(self) -> Iterator[SeaLine]:
        return (
            SeaLine(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM SeaLine WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def stops(self) -> Iterator[SeaStop]:
        return (
            SeaStop(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM SeaStop WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def docks(self) -> Iterator[SeaDock]:
        return (
            SeaDock(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaDock.i "
                "FROM (SELECT i FROM SeaStop WHERE company = :i) A "
                "LEFT JOIN SeaDock on A.i = SeaDock.stop",
                dict(i=self.i),
            ).fetchall()
        )


class SeaLine(Node):
    code = _Column[str]("code", "SeaLine")
    company = _FKColumn(SeaCompany, "company", "SeaLine")
    name = _Column[str | None]("name", "SeaLine", sourced=True)
    colour = _Column[str | None]("colour", "SeaLine", sourced=True)
    mode = _Column[str | None]("mode", "SeaLine", sourced=True)
    local = _Column[bool | None]("name", "SeaLine", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        code: str,
        company: SeaCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: str | None = None,
        local: bool | None = None,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO SeaLine (i, code, company, name, colour, mode, local) "
            "VALUES (:i, :code, :company, :name, :colour, :mode, :local)",
            dict(i=i, code=code, company=company.i, name=name, colour=colour, mode=mode, local=local),
        )
        cur.execute(
            "INSERT INTO SeaLineSource (i, source, name, colour, mode, local) "
            "VALUES (:i, :source, :name, :colour, :mode, :local)",
            dict(
                i=i,
                source=src,
                name=name is not None,
                colour=colour is not None,
                mode=mode is not None,
                local=local is not None,
            ),
        )
        return cls(conn, i)

    @property
    def docks(self) -> Iterator[SeaDock]:
        return (
            SeaDock(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaDock.i "
                'FROM (SELECT "from", "to" FROM SeaConnection WHERE line = :i) A '
                'LEFT JOIN SeaDock ON A."from" = SeaDock.i OR A."to" = SeaDock.i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def stops(self) -> Iterator[SeaStop]:
        return (
            SeaStop(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaDock.stop "
                'FROM (SELECT "from", "to" FROM SeaConnection WHERE line = :i) A '
                'LEFT JOIN SeaDock ON A."from" = SeaDock.i OR A."to" = SeaDock.i',
                dict(i=self.i),
            ).fetchall()
        )


class SeaStop(LocatedNode):
    codes = _SetAttr[str]("SeaStopCodes", "codes")
    company = _FKColumn(SeaCompany, "company", "SeaStop")
    name = _Column[str | None]("name", "SeaStop", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        codes: set[str],
        company: SeaCompany,
        name: str | None = None,
        world: str | None = None,
        coordinates: tuple[int, int] | None = None,
    ) -> Self:
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, world=world, coordinates=coordinates)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO SeaStop (i, name, company) VALUES (:i, :name, :company)",
            dict(i=i, name=name, company=company.i),
        )
        cur.executemany("INSERT INTO SeaStopCodes (i, code) VALUES (?, ?)", [(i, code) for code in codes])
        cur.execute(
            "INSERT INTO SeaStopSource (i, source, name) VALUES (:i, :source, :name)",
            dict(i=i, source=src, name=name is not None),
        )
        return cls(conn, i)

    @property
    def docks(self) -> Iterator[SeaDock]:
        return (
            SeaDock(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM SeaDock WHERE stop = :i",
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_from_here(self) -> Iterator[SeaConnection]:
        return (
            SeaConnection(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaConnection.i "
                "FROM (SELECT i FROM SeaDock WHERE stop = :i) A "
                'LEFT JOIN SeaConnection ON A.i = SeaConnection."from"',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[SeaConnection]:
        return (
            SeaConnection(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaConnection.i "
                "FROM (SELECT i FROM SeaDock WHERE stop = :i) A "
                'LEFT JOIN SeaConnection ON A.i = SeaConnection."to"',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[SeaLine]:
        return (
            SeaLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaConnection.line "
                "FROM (SELECT i FROM SeaDock WHERE stop = :i) A "
                'LEFT JOIN SeaConnection ON A.i = SeaConnection."from" OR A.i = SeaConnection."to"',
                dict(i=self.i),
            ).fetchall()
        )


class SeaDock(Node):
    code = _Column[str | None]("code", "SeaDock")
    stop = _FKColumn(SeaStop, "stop", "SeaStop")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        code: str | None,
        stop: SeaStop,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO SeaDock (i, code, stop) VALUES (:i, :code, :stop)", dict(i=i, code=code, stop=stop.i))
        cur.execute("INSERT INTO SeaDockSource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def connections_from_here(self) -> Iterator[SeaConnection]:
        return (
            SeaConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection."from" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[SeaConnection]:
        return (
            SeaConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[SeaLine]:
        return (
            SeaLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaConnection.line FROM SeaConnection "
                'WHERE SeaConnection."from" = :i OR SeaConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )


class SeaConnection(Node):
    line = _FKColumn(SeaLine, "line", "SeaConnection")
    from_ = _FKColumn(SeaDock, "from", "SeaConnection")
    to = _FKColumn(SeaDock, "to", "SeaConnection")
    direction = _Column[str | None]("direction", "SeaConnection", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        line: SeaLine,
        from_: SeaDock,
        to: SeaDock,
        direction: str | None = None,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO SeaConnection (i, line, "from", "to", direction) VALUES (:i, :line, :from_, :to, :direction)',
            dict(i=i, line=line.i, from_=from_.i, to=to.i, direction=direction),
        )
        cur.execute(
            "INSERT INTO SeaConnectionSource (i, source, direction) VALUES (:i, :source, :direction)",
            dict(i=i, source=src, direction=direction is not None),
        )
        return cls(conn, i)


class RailCompany(Node):
    name = _Column[str]("name", "RailCompany")

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, *, name: str) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO RailCompany (i, name) VALUES (:i, :name)", dict(i=i, name=name))
        cur.execute("INSERT INTO RailCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def lines(self) -> Iterator[RailLine]:
        return (
            RailLine(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM RailLine WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def stations(self) -> Iterator[RailStation]:
        return (
            RailStation(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM RailStation WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def platforms(self) -> Iterator[RailPlatform]:
        return (
            RailPlatform(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailPlatform.i "
                "FROM (SELECT i FROM RailStation WHERE company = :i) A "
                "LEFT JOIN RailPlatform on A.i = RailPlatform.station",
                dict(i=self.i),
            ).fetchall()
        )


class RailLine(Node):
    code = _Column[str]("code", "RailLine")
    company = _FKColumn(RailCompany, "company", "RailLine")
    name = _Column[str | None]("name", "RailLine", sourced=True)
    colour = _Column[str | None]("colour", "RailLine", sourced=True)
    mode = _Column[str | None]("mode", "RailLine", sourced=True)
    local = _Column[bool | None]("name", "RailLine", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        code: str,
        company: RailCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: str | None = None,
        local: bool | None = None,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO RailLine (i, code, company, name, colour, mode, local) "
            "VALUES (:i, :code, :company, :name, :colour, :mode, :local)",
            dict(i=i, code=code, company=company.i, name=name, colour=colour, mode=mode, local=local),
        )
        cur.execute(
            "INSERT INTO RailLineSource (i, source, name, colour, mode, local) "
            "VALUES (:i, :source, :name, :colour, :mode, :local)",
            dict(
                i=i,
                source=src,
                name=name is not None,
                colour=colour is not None,
                mode=mode is not None,
                local=local is not None,
            ),
        )
        return cls(conn, i)

    @property
    def platforms(self) -> Iterator[RailPlatform]:
        return (
            RailPlatform(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailPlatform.i "
                'FROM (SELECT "from", "to" FROM RailConnection WHERE line = :i) A '
                'LEFT JOIN RailPlatform ON A."from" = RailPlatform.i OR A."to" = RailPlatform.i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def stations(self) -> Iterator[RailStation]:
        return (
            RailStation(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailPlatform.station "
                'FROM (SELECT "from", "to" FROM RailConnection WHERE line = :i) A '
                'LEFT JOIN RailPlatform ON A."from" = RailPlatform.i OR A."to" = RailPlatform.i',
                dict(i=self.i),
            ).fetchall()
        )


class RailStation(LocatedNode):
    codes = _SetAttr[str]("RailStationCodes", "codes")
    company = _FKColumn(RailCompany, "company", "RailStation")
    name = _Column[str | None]("name", "RailStation", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        codes: set[str],
        company: RailCompany,
        name: str | None = None,
        world: str | None = None,
        coordinates: tuple[int, int] | None = None,
    ) -> Self:
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, world=world, coordinates=coordinates)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO RailStation (i, name, company) VALUES (:i, :name, :company)",
            dict(i=i, name=name, company=company.i),
        )
        cur.executemany("INSERT INTO RailStationCodes (i, code) VALUES (?, ?)", [(i, code) for code in codes])
        cur.execute(
            "INSERT INTO RailStationSource (i, source, name) VALUES (:i, :source, :name)",
            dict(i=i, source=src, name=name is not None),
        )
        return cls(conn, i)

    @property
    def platforms(self) -> Iterator[RailPlatform]:
        return (
            RailPlatform(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM RailPlatform WHERE station = :i",
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_from_here(self) -> Iterator[RailConnection]:
        return (
            RailConnection(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailConnection.i "
                "FROM (SELECT i FROM RailPlatform WHERE station = :i) A "
                'LEFT JOIN RailConnection ON A.i = RailConnection."from"',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[RailConnection]:
        return (
            RailConnection(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailConnection.i "
                "FROM (SELECT i FROM RailPlatform WHERE station = :i) A "
                'LEFT JOIN RailConnection ON A.i = RailConnection."to"',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[RailLine]:
        return (
            RailLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailConnection.line "
                "FROM (SELECT i FROM RailPlatform WHERE station = :i) A "
                'LEFT JOIN RailConnection ON A.i = RailConnection."from" OR A.i = RailConnection."to"',
                dict(i=self.i),
            ).fetchall()
        )


class RailPlatform(Node):
    code = _Column[str | None]("code", "RailPlatform")
    station = _FKColumn(RailStation, "station", "RailStation")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        code: str | None,
        station: RailStation,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO RailPlatform (i, code, station) VALUES (:i, :code, :station)",
            dict(i=i, code=code, station=station.i),
        )
        cur.execute("INSERT INTO RailPlatformSource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def connections_from_here(self) -> Iterator[RailConnection]:
        return (
            RailConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT RailConnection.i FROM RailConnection WHERE RailConnection."from" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[RailConnection]:
        return (
            RailConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT RailConnection.i FROM RailConnection WHERE RailConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[RailLine]:
        return (
            RailLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailConnection.line FROM RailConnection "
                'WHERE RailConnection."from" = :i OR RailConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )


class RailConnection(Node):
    line = _FKColumn(RailLine, "line", "RailConnection")
    from_ = _FKColumn(RailPlatform, "from", "RailConnection")
    to = _FKColumn(RailPlatform, "to", "RailConnection")
    direction = _Column[str | None]("direction", "RailConnection", sourced=True)

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        line: RailLine,
        from_: RailPlatform,
        to: RailPlatform,
        direction: str | None = None,
    ) -> Self:
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO RailConnection (i, line, "from", "to", direction) VALUES (:i, :line, :from_, :to, :direction)',
            dict(i=i, line=line.i, from_=from_.i, to=to.i, direction=direction),
        )
        cur.execute(
            "INSERT INTO RailConnectionSource (i, source, direction) VALUES (:i, :source, :direction)",
            dict(i=i, source=src, direction=direction is not None),
        )
        return cls(conn, i)


class SpawnWarp(LocatedNode):
    name = _Column[str]("name", "SpawnWarp")
    warp_type = _Column[str]("warpType", "SpawnWarp")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        name: str,
        warp_type: str,
        world: str | None = None,
        coordinates: tuple[int, int] | None = None,
    ) -> Self:
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, world=world, coordinates=coordinates)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO SpawnWarp (i, name, warpType) VALUES (:i, :name, :warp_type)",
            dict(i=i, name=name, warp_type=warp_type),
        )
        return cls(conn, i)


class Town(LocatedNode):
    name = _Column[str]("name", "Town")
    rank = _Column[str]("rank", "Town")
    mayor = _Column[str]("mayor", "Town")
    deputy_mayor = _Column[str | None]("deputyMayor", "Town")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        name: str,
        rank: str,
        mayor: str,
        deputy_mayor: str | None,
        world: str | None = None,
        coordinates: tuple[int, int] | None = None,
    ) -> Self:
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, world=world, coordinates=coordinates)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Town (i, name, rank, mayor, deputyMayor) VALUES (:i, :name, :rank, :mayor, :deputy_mayor)",
            dict(i=i, name=name, rank=rank, mayor=mayor, deputy_mayor=deputy_mayor),
        )
        return cls(conn, i)


if __name__ == "__main__":
    gd = GD.create(["Temp"])
