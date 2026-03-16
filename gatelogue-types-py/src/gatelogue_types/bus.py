from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, NotRequired, Required, Self, TypedDict, Unpack

from gatelogue_types._util import _Column, _FKColumn, _format_code, _format_str, _SetAttr
from gatelogue_types.node import LocatedNode, Node

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterator

type BusMode = Literal["warp", "traincarts"]


class BusCompany(Node):
    name = _Column[str]("name", "BusCompany", formatter=_format_str)
    """Name of the bus company"""
    link = _Column[str | None]("link", "BusCompany", sourced=True, formatter=_format_str)
    """Link to the MRT Wiki page for the company"""
    COLUMNS: ClassVar = (name, link)

    def __str__(self):
        return super().__str__() + f" {self.name}"

    class CreateParams(TypedDict, total=False):
        """Internal use"""

        name: Required[str]
        link: str | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        """Internal use"""
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO BusCompany (i, name, link) VALUES (:i, :name, :link)", dict(i=i, **kwargs))
        cur.execute("INSERT INTO BusCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src, **kwargs))
        return cls(conn, i)

    @property
    def lines(self) -> Iterator[BusLine]:
        """List of all :py:class:`BusLine` s the company operates"""
        return self._sql_derived("bus/company_lines", BusLine)

    @property
    def stops(self) -> Iterator[BusStop]:
        """List of all :py:class:`BusStop` s the company's lines stop at"""
        return self._sql_derived("bus/company_stops", BusStop)

    @property
    def berths(self) -> Iterator[BusBerth]:
        """List of all :py:class:`BusBerth` s the company's lines stop at"""
        return self._sql_derived("bus/company_berths", BusBerth)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM BusCompany WHERE name = ?", (self.name,)).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE BusLine SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE BusStop SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))


class BusLine(Node):
    code = _Column[str]("code", "BusLine", formatter=_format_str)
    """Unique code identifying the bus line"""
    company = _FKColumn(BusCompany, "company", "BusLine")
    """The :py:class:`BusCompany` that operates the line"""
    name = _Column[str | None]("name", "BusLine", sourced=True, formatter=_format_str)
    """Name of the line"""
    colour = _Column[str | None]("colour", "BusLine", sourced=True, formatter=_format_str)
    """Colour of the line (on a map)"""
    mode = _Column[BusMode | None]("mode", "BusLine", sourced=True, formatter=_format_str)
    """Type of bus vehicle or technology the line uses"""
    local = _Column[bool | None]("local", "BusLine", sourced=True)
    """Whether the line operates within the city, e.g. a local bus service"""
    COLUMNS: ClassVar = (code, company, name, colour, mode, local)

    def __str__(self):
        return super().__str__() + f" {self.company.name} {self.code}"

    class CreateParams(TypedDict, total=False):
        """Internal use"""

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
        """Internal use"""
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
        return self._sql_derived("bus/line_berths", BusBerth)

    @property
    def stops(self) -> Iterator[BusStop]:
        """List of all :py:class:`BusStop` s the line stops at"""
        return self._sql_derived("bus/line_stops", BusStop)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM BusLine WHERE code = ? AND company = ?", (self.code, self.company.i)
            ).fetchall()
        )

    def _merge(self, other: Self):
        self.conn.execute("UPDATE BusConnection SET line = :i1 WHERE line = :i2", dict(i1=self.i, i2=other.i))


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
        """Internal use"""
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
        return self._sql_derived("bus/stop_berths", BusBerth)

    @property
    def connections_from_here(self) -> Iterator[BusConnection]:
        """List of all :py:class:`BusConnections` s departing from this stop"""
        return self._sql_derived("bus/stop_connections_from_here", BusConnection)

    @property
    def connections_to_here(self) -> Iterator[BusConnection]:
        """List of all :py:class:`BusConnections` s arriving at this stop"""
        return self._sql_derived("bus/stop_connections_to_here", BusConnection)

    @property
    def lines(self) -> Iterator[BusLine]:
        """List of all :py:class:`BusLines` s at this stop"""
        return self._sql_derived("bus/stop_lines", BusLine)

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
        self.conn.execute("UPDATE BusBerth SET stop = :i1 WHERE stop = :i2", dict(i1=self.i, i2=other.i))
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
        """Internal use"""
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO BusBerth (i, code, stop) VALUES (:i, :code, :stop)", dict(i=i, **kwargs))
        cur.execute("INSERT INTO BusBerthSource (i, source) VALUES (:i, :source)", dict(i=i, source=src, **kwargs))
        return cls(conn, i)

    @property
    def connections_from_here(self) -> Iterator[BusConnection]:
        """List of all :py:class:`BusConnections` s departing from this berth"""
        return self._sql_derived("bus/berth_connections_from_here", BusConnection)

    @property
    def connections_to_here(self) -> Iterator[BusConnection]:
        """List of all :py:class:`BusConnections` s arriving at this berth"""
        return self._sql_derived("bus/berth_connections_to_here", BusConnection)

    @property
    def lines(self) -> Iterator[BusLine]:
        """List of all :py:class:`BusLines` s at this stop"""
        return self._sql_derived("bus/berth_lines", BusLine)

    def equivalent_nodes(self) -> Iterator[Self]:
        if (code := self.code) is None:
            return iter(())
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM BusBerth WHERE stop = ? AND code = ?", (self.stop.i, code)
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute('UPDATE BusConnection SET "from" = :i1 WHERE "from" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute('UPDATE BusConnection SET "to" = :i1 WHERE "to" = :i2', dict(i1=self.i, i2=other.i))


class BusConnection(Node):
    line = _FKColumn(BusLine, "line", "BusConnection")
    """The :py:class:`BusLine` that the connection is made on"""
    from_ = _FKColumn(BusBerth, "from", "BusConnection")
    """The :py:class:`BusBerth` the connection departs from"""
    to = _FKColumn(BusBerth, "to", "BusConnection")
    """The :py:class:`BusBerth` the connection arrives at"""
    direction = _Column[str | None]("direction", "BusConnection", sourced=True, formatter=_format_str)
    """The direction taken when travelling along this connection, e.g. ``Eastbound``, ``towards Terminus Name``"""
    duration = _Column[int | None]("duration", "BusConnection", sourced=True, formatter=_format_str)
    """The duration taken in seconds to travel on this connection"""
    COLUMNS: ClassVar = (line, from_, to, direction, duration)

    def __str__(self):
        return super().__str__() + f" {self.line.company.name} {self.line.code} {self.from_.code} -> {self.to.code}"

    class CreateParams(TypedDict):
        line: BusLine
        from_: BusBerth
        to: BusBerth
        direction: NotRequired[str | None]
        duration: NotRequired[int | None]

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        """Internal use"""
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO BusConnection (i, line, "from", "to", direction, duration) '
            'VALUES (:i, :line, :from_, :to, :direction, :duration)',
            dict(i=i, **kwargs),
        )
        cur.execute(
            "INSERT INTO BusConnectionSource (i, source, direction, duration) "
            "VALUES (:i, :source, :direction_src, :duration_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @classmethod
    def create2(
        cls, conn: sqlite3.Connection, src: int, *, direction2: str | None = None, **kwargs: Unpack[CreateParams]
    ) -> tuple[Self, Self]:
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
