from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from typing import Literal, NotRequired, Required, Self, TypedDict, Unpack

from gatelogue_types.base import _Column, _FKColumn, _SetAttr
from gatelogue_types.node import LocatedNode, Node

type SeaMode = Literal["cruise", "warp ferry", "traincarts ferry"]


class SeaCompany(Node):
    name = _Column[str]("name", "SeaCompany")
    """Name of the sea company"""

    class CreateParams(TypedDict):
        name: str

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        name = kwargs["name"]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO SeaCompany (i, name) VALUES (:i, :name)", dict(i=i, name=name))
        cur.execute("INSERT INTO SeaCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def lines(self) -> Iterator[SeaLine]:
        """List of all :py:class:`SeaLine` s the company operates"""
        return (
            SeaLine(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM SeaLine WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def stops(self) -> Iterator[SeaStop]:
        """List of all :py:class:`SeaStop` s the company's lines stop at"""
        return (
            SeaStop(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM SeaStop WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def docks(self) -> Iterator[SeaDock]:
        """List of all :py:class:`SeaDock` s the company's lines stop at"""
        return (
            SeaDock(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaDock.i "
                "FROM (SELECT i FROM SeaStop WHERE company = :i) A "
                "LEFT JOIN SeaDock on A.i = SeaDock.stop",
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM SeaCompany WHERE name = ?", (self.name,)).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE SeaLine SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE SeaStop SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaCompanySource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaCompany WHERE i = :i2", dict(i1=self.i, i2=other.i))


class SeaLine(Node):
    code = _Column[str]("code", "SeaLine")
    """Unique code identifying the sea line"""
    company = _FKColumn(SeaCompany, "company", "SeaLine")
    """The :py:class:`SeaCompany` that operates the line"""
    name = _Column[str | None]("name", "SeaLine", sourced=True)
    """Name of the line"""
    colour = _Column[str | None]("colour", "SeaLine", sourced=True)
    """Colour of the line (on a map)"""
    mode = _Column[str | None]("mode", "SeaLine", sourced=True)
    """Type of sea vehicle or technology the line uses"""
    local = _Column[bool | None]("name", "SeaLine", sourced=True)
    """Whether the company operates within the city, e.g. a local ferry service"""

    class CreateParams(TypedDict, total=False):
        code: Required[str]
        company: Required[SeaCompany]
        name: str | None
        colour: str | None
        mode: BusMode | None
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
        """List of all :py:class:`SeaDocks` s the line stops at"""
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
        """List of all :py:class:`SeaStop` s the line stops at"""
        return (
            SeaStop(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaDock.stop "
                'FROM (SELECT "from", "to" FROM SeaConnection WHERE line = :i) A '
                'LEFT JOIN SeaDock ON A."from" = SeaDock.i OR A."to" = SeaDock.i',
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM SeaLine WHERE code = ? AND company = ?", (self.code, self.company.i)
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE SeaConnection SET line = :i1 WHERE line = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaLineSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaLine WHERE i = :i2", dict(i1=self.i, i2=other.i))


class SeaStop(LocatedNode):
    codes = _SetAttr[str]("SeaStopCodes", "code")
    """Unique code(s) identifying the sea stop. May also be the same as the name"""
    company = _FKColumn(SeaCompany, "company", "SeaStop")
    """The :py:class:`SeaCompany` that owns this stop"""
    name = _Column[str | None]("name", "SeaStop", sourced=True)
    """Name of the stop"""

    class CreateParams(LocatedNode.CreateParams, total=False):
        codes: Required[set[str]]
        company: Required[SeaCompany]
        name: str | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        codes, company, name = kwargs["codes"], kwargs["company"], kwargs.get("name")
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
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
        """List of :py:class:`SeaDock` s this stop has"""
        return (
            SeaDock(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM SeaDock WHERE stop = :i",
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_from_here(self) -> Iterator[SeaConnection]:
        """List of all :py:class:`SeaConnections` s departing from this stop"""
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
        """List of all :py:class:`SeaConnections` s arriving at this stop"""
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
        """List of all :py:class:`SeaLines` s at this stop"""
        return (
            SeaLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaConnection.line "
                "FROM (SELECT i FROM SeaDock WHERE stop = :i) A "
                'LEFT JOIN SeaConnection ON A.i = SeaConnection."from" OR A.i = SeaConnection."to"',
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
                "SELECT DISTINCT SeaStop.i "
                "FROM SeaStop LEFT JOIN SeaStopCodes ON SeaStop.i = SeaStopCodes.i "
                f"WHERE company = ? AND SeaStopCodes.code IN ({code_params})",
                (
                    self.company.i,
                    *codes,
                ),
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE SeaDock SET stop = :i1 WHERE stop = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaStopSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaStop WHERE i = :i2", dict(i1=self.i, i2=other.i))
        super()._merge(other)


class SeaDock(Node):
    code = _Column[str | None]("code", "SeaDock")
    """Unique code identifying the dock. May not necessarily be the same as the code ingame. If ``None``, code is unspecified"""
    stop = _FKColumn(SeaStop, "stop", "SeaStop")
    """The :py:class:`SeaStop` of the dock"""

    class CreateParams(TypedDict):
        code: str | None
        stop: SeaStop

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        code, stop = kwargs["code"], kwargs["stop"]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO SeaDock (i, code, stop) VALUES (:i, :code, :stop)", dict(i=i, code=code, stop=stop.i))
        cur.execute("INSERT INTO SeaDockSource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
        return cls(conn, i)

    @property
    def connections_from_here(self) -> Iterator[SeaConnection]:
        """List of all :py:class:`SeaConnection` s departing from this dock"""
        return (
            SeaConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection."from" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[SeaConnection]:
        """List of all :py:class:`SeaConnection` s arriving at this dock"""
        return (
            SeaConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[SeaLine]:
        """List of all :py:class:`SeaLine` s at this dock"""
        return (
            SeaLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT SeaConnection.line FROM SeaConnection "
                'WHERE SeaConnection."from" = :i OR SeaConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        if (code := self.code) is None:
            return iter(())
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM SeaDock WHERE stop = ? AND code = ?", (self.stop, code)
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute('UPDATE SeaConnection SET "from" = :i1 WHERE "from" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute('UPDATE SeaConnection SET "to" = :i1 WHERE "to" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaDockSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaDock WHERE i = :i2", dict(i1=self.i, i2=other.i))


class SeaConnection(Node):
    line = _FKColumn(SeaLine, "line", "SeaConnection")
    """The :py:class:`SeaLine` that the connection is made on"""
    from_ = _FKColumn(SeaDock, "from", "SeaConnection")
    """The :py:class:`SeaDock` the connection departs from"""
    to = _FKColumn(SeaDock, "to", "SeaConnection")
    """The :py:class:`SeaDock` the connection arrives at"""
    direction = _Column[str | None]("direction", "SeaConnection", sourced=True)
    """The direction taken when travelling along this connection, e.g. ``Eastbound``, ``towards Terminus Name``"""

    class CreateParams(TypedDict):
        line: SeaLine
        from_: SeaDock
        to: SeaDock
        direction: NotRequired[str | None]

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        line, from_, to, direction = kwargs["line"], kwargs["from_"], kwargs["to"], kwargs.get("direction")
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

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT i FROM SeaConnection WHERE line = ? AND "from" = ? AND "to" = ?',
                (self.line.i, self.from_.i, self.to.i),
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM SeaConnectionSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM SeaConnection WHERE i = :i2", dict(i1=self.i, i2=other.i))
