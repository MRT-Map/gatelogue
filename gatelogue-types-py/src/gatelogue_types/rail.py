from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from typing import Literal, NotRequired, Required, Self, TypedDict, Unpack

from gatelogue_types.base import _Column, _FKColumn, _SetAttr
from gatelogue_types.node import LocatedNode, Node

type RailMode = Literal["warp", "cart", "traincarts", "vehicles"]


class RailCompany(Node):
    name = _Column[str]("name", "RailCompany")
    """Name of the rail company"""

    class CreateParams(TypedDict):
        name: str

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        name = kwargs["name"]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO RailCompany (i, name) VALUES (:i, :name)", dict(i=i, name=name))
        cur.execute("INSERT INTO RailCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def lines(self) -> Iterator[RailLine]:
        """List of all :py:class:`RailLine` s the company operates"""
        return (
            RailLine(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM RailLine WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def stations(self) -> Iterator[RailStation]:
        """List of all :py:class:`RailStation` s the company's lines stop at"""
        return (
            RailStation(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM RailStation WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def platforms(self) -> Iterator[RailPlatform]:
        """List of all :py:class:`RailPltaform` s the company's lines stop at"""
        return (
            RailPlatform(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailPlatform.i "
                "FROM (SELECT i FROM RailStation WHERE company = :i) A "
                "LEFT JOIN RailPlatform on A.i = RailPlatform.station",
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM RailCompany WHERE name = ?", (self.name,)).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE RailLine SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE RailStation SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailCompanySource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailCompany WHERE i = :i2", dict(i1=self.i, i2=other.i))


class RailLine(Node):
    code = _Column[str]("code", "RailLine")
    """Unique code identifying the rail line"""
    company = _FKColumn(RailCompany, "company", "RailLine")
    """The :py:class:`RailCompany` that operates the line"""
    name = _Column[str | None]("name", "RailLine", sourced=True)
    """Name of the line"""
    colour = _Column[str | None]("colour", "RailLine", sourced=True)
    """Colour of the line (on a map)"""
    mode = _Column[str | None]("mode", "RailLine", sourced=True)
    """Type of rail vehicle or technology the line uses"""
    local = _Column[bool | None]("name", "RailLine", sourced=True)
    """Whether the company operates within the city, e.g. a local ferry service"""

    class CreateParams(TypedDict, total=False):
        code: Required[str]
        company: Required[RailCompany]
        name: str | None
        colour: str | None
        mode: RailMode | None
        local: bool | None

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        **kwargs: Unpack[CreateParams],
    ) -> Self:
        code, company, name, colour, mode, local = (
            kwargs["code"],
            kwargs["company"],
            kwargs.get("name"),
            kwargs.get("colour"),
            kwargs.get("mode"),
            kwargs.get("local"),
        )
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
        """List of all :py:class:`RailPlatform` s the line stops at"""
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
        """List of all :py:class:`RailStation` s the line stops at"""
        return (
            RailStation(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailPlatform.station "
                'FROM (SELECT "from", "to" FROM RailConnection WHERE line = :i) A '
                'LEFT JOIN RailPlatform ON A."from" = RailPlatform.i OR A."to" = RailPlatform.i',
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM RailLine WHERE code = ? AND company = ?", (self.code, self.company.i)
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE RailConnection SET line = :i1 WHERE line = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailLineSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailLine WHERE i = :i2", dict(i1=self.i, i2=other.i))


class RailStation(LocatedNode):
    codes = _SetAttr[str]("RailStationCodes", "code")
    """Unique code(s) identifying the rail station. May also be the same as the name"""
    company = _FKColumn(RailCompany, "company", "RailStation")
    """The :py:class:`RailCompany` that owns this stop"""
    name = _Column[str | None]("name", "RailStation", sourced=True)
    """Name of the station"""

    class CreateParams(LocatedNode.CreateParams, total=False):
        codes: Required[set[str]]
        company: Required[RailCompany]
        name: str | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        codes, company, name = kwargs["codes"], kwargs["company"], kwargs.get("name")
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
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
        """List of :py:class:`RailPlatform` s this stop has"""
        return (
            RailPlatform(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM RailPlatform WHERE station = :i",
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_from_here(self) -> Iterator[RailConnection]:
        """List of all :py:class:`RailConnection` s departing from this station"""
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
        """List of all :py:class:`RailConnection` s arriving at this station"""
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
        """List of all :py:class:`RailLine` s at this stop"""
        return (
            RailLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailConnection.line "
                "FROM (SELECT i FROM RailPlatform WHERE station = :i) A "
                'LEFT JOIN RailConnection ON A.i = RailConnection."from" OR A.i = RailConnection."to"',
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        if len(codes := self.codes) == 0:
            return iter(())
        code_params = "?, " * (len(codes) - 1) + "?"
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailStation.i "
                "FROM RailStation LEFT JOIN RailStationCodes ON RailStation.i = RailStationCodes.i "
                f"WHERE company = ? AND RailStationCodes.code IN ({code_params})",
                (
                    self.company.i,
                    *codes,
                ),
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE RailPlatform SET station = :i1 WHERE station = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailStationSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailStation WHERE i = :i2", dict(i1=self.i, i2=other.i))
        super()._merge(other)


class RailPlatform(Node):
    code = _Column[str | None]("code", "RailPlatform")
    """Unique code identifying the platform. May not necessarily be the same as the code ingame.
    If ``None``, code is unspecified"""
    station = _FKColumn(RailStation, "station", "RailStation")
    """The :py:class:`RailPlatform` of the dock"""

    class CreateParams(TypedDict):
        code: str | None
        station: RailStation

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        code, station = kwargs["code"], kwargs["station"]
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
        """List of all :py:class:`RailConnection` s departing from this platform"""
        return (
            RailConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT RailConnection.i FROM RailConnection WHERE RailConnection."from" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[RailConnection]:
        """List of all :py:class:`RailConnection` s arriving at this platform"""
        return (
            RailConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT RailConnection.i FROM RailConnection WHERE RailConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[RailLine]:
        """List of all :py:class:`RailLine` s at this platform"""
        return (
            RailLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT RailConnection.line FROM RailConnection "
                'WHERE RailConnection."from" = :i OR RailConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        if (code := self.code) is None:
            return iter(())
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM RailPlatform WHERE station = ? AND code = ?", (self.station, code)
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute('UPDATE RailConnection SET "from" = :i1 WHERE "from" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute('UPDATE RailConnection SET "to" = :i1 WHERE "to" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailPlatformSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailPlatform WHERE i = :i2", dict(i1=self.i, i2=other.i))


class RailConnection(Node):
    line = _FKColumn(RailLine, "line", "RailConnection")
    """The :py:class:`RailLine` that the connection is made on"""
    from_ = _FKColumn(RailPlatform, "from", "RailConnection")
    """The :py:class:`RailLine` the connection departs from"""
    to = _FKColumn(RailPlatform, "to", "RailConnection")
    """The :py:class:`RailLine` the connection arrives at"""
    direction = _Column[str | None]("direction", "RailConnection", sourced=True)
    """The direction taken when travelling along this connection, e.g. ``Eastbound``, ``towards Terminus Name``"""

    class CreateParams(TypedDict):
        line: RailLine
        from_: RailPlatform
        to: RailPlatform
        direction: NotRequired[str | None]

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        line, from_, to, direction = kwargs["line"], kwargs["from_"], kwargs["to"], kwargs.get("direction")
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

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT i FROM RailConnection WHERE line = ? AND "from" = ? AND "to" = ?',
                (self.line.i, self.from_.i, self.to.i),
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM RailConnectionSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM RailConnection WHERE i = :i2", dict(i1=self.i, i2=other.i))
