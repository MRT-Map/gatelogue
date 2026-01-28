from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, NotRequired, Required, Self, TypedDict, Unpack

from gatelogue_types.base import _Column, _FKColumn, _format_code, _format_str, _SetAttr
from gatelogue_types.node import LocatedNode, Node

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterator

type BusMode = Literal["warp", "traincarts"]


class BusCompany(Node):
    name = _Column[str]("name", "BusCompany", formatter=_format_str)
    """Name of the bus company"""
    COLUMNS: ClassVar = (name,)

    def __str__(self):
        return super().__str__() + f" {self.name}"

    class CreateParams(TypedDict):
        name: str

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO BusCompany (i, name) VALUES (:i, :name)", dict(i=i, **kwargs))
        cur.execute("INSERT INTO BusCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src, **kwargs))
        return cls(conn, i)

    @property
    def lines(self) -> Iterator[BusLine]:
        """List of all :py:class:`BusLine` s the company operates"""
        return (
            BusLine(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM BusLine WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def stops(self) -> Iterator[BusStop]:
        """List of all :py:class:`BusStop` s the company's lines stop at"""
        return (
            BusStop(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM BusStop WHERE company = :i", dict(i=self.i)).fetchall()
        )

    @property
    def berths(self) -> Iterator[BusBerth]:
        """List of all :py:class:`BusBerth` s the company's lines stop at"""
        return (
            BusBerth(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusBerth.i "
                "FROM (SELECT i FROM BusStop WHERE company = :i) A "
                "LEFT JOIN BusBerth on A.i = BusBerth.stop",
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM BusCompany WHERE name = ?", (self.name,)).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE BusLine SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE BusStop SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusCompanySource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusCompany WHERE i = :i2", dict(i1=self.i, i2=other.i))


class BusLine(Node):
    code = _Column[str]("code", "BusLine", formatter=_format_code)
    """Unique code identifying the bus line"""
    company = _FKColumn(BusCompany, "company", "BusLine")
    """The :py:class:`BusCompany` that operates the line"""
    name = _Column[str | None]("name", "BusLine", sourced=True, formatter=_format_str)
    """Name of the line"""
    colour = _Column[str | None]("colour", "BusLine", sourced=True, formatter=_format_str)
    """Colour of the line (on a map)"""
    mode = _Column[str | None]("mode", "BusLine", sourced=True, formatter=_format_str)
    """Type of bus vehicle or technology the line uses"""
    local = _Column[bool | None]("local", "BusLine", sourced=True)
    """Whether the line operates within the city, e.g. a local bus service"""
    COLUMNS: ClassVar = (code, company, name, colour, mode, local)

    def __str__(self):
        return super().__str__() + f" {self.company.name} {self.code}"

    class CreateParams(TypedDict, total=False):
        code: Required[str]
        company: Required[BusCompany]
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
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO BusLine (i, code, company, name, colour, mode, local) "
            "VALUES (:i, :code, :company, :name, :colour, :mode, :local)",
            dict(i=i, **kwargs),
        )
        cur.execute(
            "INSERT INTO BusLineSource (i, source, name, colour, mode, local) "
            "VALUES (:i, :source, :name_src, :colour_src, :mode_src, :local_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @property
    def berths(self) -> Iterator[BusBerth]:
        """List of all :py:class:`BusBerths` s the line stops at"""
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
        """List of all :py:class:`BusStop` s the line stops at"""
        return (
            BusStop(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusBerth.stop "
                'FROM (SELECT "from", "to" FROM BusConnection WHERE line = :i) A '
                'LEFT JOIN BusBerth ON A."from" = BusBerth.i OR A."to" = BusBerth.i',
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM BusLine WHERE code = ? AND company = ?", (self.code, self.company.i)
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE BusConnection SET line = :i1 WHERE line = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusLineSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusLine WHERE i = :i2", dict(i1=self.i, i2=other.i))


class BusStop(LocatedNode):
    codes = _SetAttr[str]("BusStopCodes", "code", formatter=_format_code)
    """Unique code(s) identifying the bus stop. May also be the same as the name"""
    company = _FKColumn(BusCompany, "company", "BusStop")
    """The :py:class:`BusCompany` that owns this stop"""
    name = _Column[str | None]("name", "BusStop", sourced=True, formatter=_format_str)
    """Name of the stop"""
    COLUMNS: ClassVar = (*LocatedNode.COLUMNS, codes, company, name)

    def __str__(self):
        return super().__str__() + f" {self.company.name} {'/'.join(self.codes)}"

    class CreateParams(LocatedNode.CreateParams, total=False):
        codes: Required[set[str]]
        company: Required[BusCompany]
        name: str | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        kwargs = cls.format_create_kwargs(**kwargs)
        codes = kwargs.get("codes", set())
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO BusStop (i, name, company) VALUES (:i, :name, :company)",
            dict(i=i, **kwargs),
        )
        cur.executemany("INSERT INTO BusStopCodes (i, code) VALUES (?, ?)", [(i, code) for code in codes])
        cur.execute(
            "INSERT INTO BusStopSource (i, source, name) VALUES (:i, :source, :name_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @property
    def berths(self) -> Iterator[BusBerth]:
        """List of :py:class:`BusBerths` s this stop has"""
        return (
            BusBerth(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM BusBerth WHERE stop = :i",
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_from_here(self) -> Iterator[BusConnection]:
        """List of all :py:class:`BusConnections` s departing from this stop"""
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
        """List of all :py:class:`BusConnections` s arriving at this stop"""
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
        """List of all :py:class:`BusLines` s at this stop"""
        return (
            BusLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusConnection.line "
                "FROM (SELECT i FROM BusBerth WHERE stop = :i) A "
                'LEFT JOIN BusConnection ON A.i = BusConnection."from" OR A.i = BusConnection."to"',
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
                "SELECT DISTINCT BusStop.i "
                "FROM BusStop LEFT JOIN BusStopCodes ON BusStop.i = BusStopCodes.i "
                f"WHERE company = ? AND BusStopCodes.code IN ({code_params})",
                (
                    self.company.i,
                    *codes,
                ),
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE BusBerth SET stop = :i1 WHERE stop = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusStopSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusStop WHERE i = :i2", dict(i1=self.i, i2=other.i))
        super()._merge(other)


class BusBerth(Node):
    code = _Column[str | None]("code", "BusBerth", formatter=_format_code)
    """Unique code identifying the berth. May not necessarily be the same as the code ingame. If ``None``, code is unspecified"""
    stop = _FKColumn(BusStop, "stop", "BusBerth")
    """The :py:class:`BusStop` of the berth"""
    COLUMNS: ClassVar = (code, stop)

    def __str__(self):
        return super().__str__() + f" {self.stop.company.name} {'/'.join(self.stop.codes)} {self.code}"

    class CreateParams(TypedDict):
        code: str | None
        stop: BusStop

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO BusBerth (i, code, stop) VALUES (:i, :code, :stop)", dict(i=i, **kwargs))
        cur.execute("INSERT INTO BusBerthSource (i, source) VALUES (:i, :source)", dict(i=i, source=src, **kwargs))
        return cls(conn, i)

    @property
    def connections_from_here(self) -> Iterator[BusConnection]:
        """List of all :py:class:`BusConnections` s departing from this berth"""
        return (
            BusConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT BusConnection.i FROM BusConnection WHERE BusConnection."from" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def connections_to_here(self) -> Iterator[BusConnection]:
        """List of all :py:class:`BusConnections` s arriving at this berth"""
        return (
            BusConnection(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT BusConnection.i FROM BusConnection WHERE BusConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    @property
    def lines(self) -> Iterator[BusLine]:
        """List of all :py:class:`BusLines` s at this stop"""
        return (
            BusLine(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT BusConnection.line FROM BusConnection "
                'WHERE BusConnection."from" = :i OR BusConnection."to" = :i',
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        if (code := self.code) is None:
            return iter(())
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM BusBerth WHERE stop = ? AND code = ?", (self.stop, code)
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute('UPDATE BusConnection SET "from" = :i1 WHERE "from" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute('UPDATE BusConnection SET "to" = :i1 WHERE "to" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusBerthSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusBerth WHERE i = :i2", dict(i1=self.i, i2=other.i))


class BusConnection(Node):
    line = _FKColumn(BusLine, "line", "BusConnection")
    """The :py:class:`BusLine` that the connection is made on"""
    from_ = _FKColumn(BusBerth, "from", "BusConnection")
    """The :py:class:`BusBerth` the connection departs from"""
    to = _FKColumn(BusBerth, "to", "BusConnection")
    """The :py:class:`BusBerth` the connection arrives at"""
    direction = _Column[str | None]("direction", "BusConnection", sourced=True, formatter=_format_str)
    """The direction taken when travelling along this connection, e.g. ``Eastbound``, ``towards Terminus Name``"""
    COLUMNS: ClassVar = (line, from_, to, direction)

    def __str__(self):
        return super().__str__() + f" {self.line.company.name} {self.line.code} {self.from_.code} -> {self.to.code}"

    class CreateParams(TypedDict):
        line: BusLine
        from_: BusBerth
        to: BusBerth
        direction: NotRequired[str | None]

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO BusConnection (i, line, "from", "to", direction) VALUES (:i, :line, :from_, :to, :direction)',
            dict(i=i, **kwargs),
        )
        cur.execute(
            "INSERT INTO BusConnectionSource (i, source, direction) VALUES (:i, :source, :direction_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @classmethod
    def create2(cls, conn: sqlite3.Connection, src: int, *, direction2: str | None = None, **kwargs: Unpack[CreateParams]) -> tuple[Self, Self]:
        kwargs2 = kwargs.copy()
        kwargs2["from_"], kwargs2["to"] = kwargs2["to"], kwargs2["from"]
        kwargs2["direction"] = direction2 or kwargs2["direction"]
        return cls.create(conn, src, **kwargs), cls.create(conn, src, **kwargs2)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT i FROM BusConnection WHERE line = ? AND "from" = ? AND "to" = ?',
                (self.line.i, self.from_.i, self.to.i),
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM BusConnectionSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM BusConnection WHERE i = :i2", dict(i1=self.i, i2=other.i))
