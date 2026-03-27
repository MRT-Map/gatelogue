from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, NotRequired, Required, Self, TypedDict, Unpack

from gatelogue_types._util import _Column, _FKColumn, _format_code, _format_str, _SetAttr
from gatelogue_types.node import LocatedNode, Node

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterator

type RailMode = Literal["warp", "cart", "traincarts", "vehicles"]


class RailCompany(Node):
    name = _Column[str]("name", "RailCompany", formatter=_format_str)
    """Name of the rail company"""
    link = _Column[str | None]("link", "RailCompany", sourced=True, formatter=_format_str)
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
        kwargs = cls.format_create_kwargs(**kwargs)  # pyrefly: ignore[bad-assignment]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO RailCompany (i, name, link) VALUES (:i, :name, :link)", dict(i=i, **kwargs))
        cur.execute("INSERT INTO RailCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src, **kwargs))
        return cls(conn, i)

    @property
    def lines(self) -> Iterator[RailLine]:
        """List of all :py:class:`RailLine` s the company operates"""
        return self._sql_derived("rail/company_lines", RailLine)

    @property
    def stations(self) -> Iterator[RailStation]:
        """List of all :py:class:`RailStation` s the company's lines stop at"""
        return self._sql_derived("rail/company_stations", RailStation)

    @property
    def platforms(self) -> Iterator[RailPlatform]:
        """List of all :py:class:`RailPlatform` s the company's lines stop at"""
        return self._sql_derived("rail/company_platforms", RailPlatform)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM RailCompany WHERE name = ?", (self.name,)).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE RailLine SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE RailStation SET company = :i1 WHERE company = :i2", dict(i1=self.i, i2=other.i))


class RailLine(Node):
    code = _Column[str]("code", "RailLine", formatter=_format_str)
    """Unique code identifying the rail line"""
    company = _FKColumn(RailCompany, "company", "RailLine")
    """The :py:class:`RailCompany` that operates the line"""
    name = _Column[str | None]("name", "RailLine", sourced=True, formatter=_format_str)
    """Name of the line"""
    colour = _Column[str | None]("colour", "RailLine", sourced=True, formatter=_format_str)
    """Colour of the line (on a map)"""
    mode = _Column[str | None]("mode", "RailLine", sourced=True, formatter=_format_str)
    """Type of rail vehicle or technology the line uses"""
    local = _Column[bool | None]("local", "RailLine", sourced=True)
    """Whether the company operates within the city, e.g. a local ferry service"""
    COLUMNS: ClassVar = (code, company, name, colour, mode, local)

    def __str__(self):
        return super().__str__() + f" {self.company.name} {self.code}"

    class CreateParams(TypedDict, total=False):
        """Internal use"""

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
        """Internal use"""
        kwargs = cls.format_create_kwargs(**kwargs)  # pyrefly: ignore[bad-assignment]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO RailLine (i, code, company, name, colour, mode, local) "
            "VALUES (:i, :code, :company, :name, :colour, :mode, :local)",
            dict(i=i, **kwargs),
        )
        cur.execute(
            "INSERT INTO RailLineSource (i, source, name, colour, mode, local) "
            "VALUES (:i, :source, :name_src, :colour_src, :mode_src, :local_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @property
    def platforms(self) -> Iterator[RailPlatform]:
        """List of all :py:class:`RailPlatform` s the line stops at"""
        return self._sql_derived("rail/line_platforms", RailPlatform)

    @property
    def stations(self) -> Iterator[RailStation]:
        """List of all :py:class:`RailStation` s the line stops at"""
        return self._sql_derived("rail/line_stations", RailStation)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM RailLine WHERE code = ? AND company = ?", (self.code, self.company.i)
            ).fetchall()
        )

    def _merge(self, other: Self):
        self.conn.execute("UPDATE RailConnection SET line = :i1 WHERE line = :i2", dict(i1=self.i, i2=other.i))


class RailStation(LocatedNode):
    codes = _SetAttr[str]("RailStationCodes", "code", formatter=_format_code)
    """Unique code(s) identifying the rail station. May also be the same as the name"""
    company = _FKColumn(RailCompany, "company", "RailStation")
    """The :py:class:`RailCompany` that owns this stop"""
    name = _Column[str | None]("name", "RailStation", sourced=True, formatter=_format_str)
    """Name of the station"""
    COLUMNS: ClassVar = (*LocatedNode.COLUMNS, codes, company, name)

    def __str__(self):
        return super().__str__() + f" {self.company.name} {'/'.join(self.codes)}"

    class CreateParams(LocatedNode.CreateParams, total=False):
        codes: Required[set[str]]
        company: Required[RailCompany]
        name: str | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        """Internal use"""
        kwargs = cls.format_create_kwargs(**kwargs)  # pyrefly: ignore[bad-assignment]
        codes = kwargs.get("codes", set())
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO RailStation (i, name, company) VALUES (:i, :name, :company)",
            dict(i=i, **kwargs),
        )
        cur.executemany("INSERT INTO RailStationCodes (i, code) VALUES (?, ?)", [(i, code) for code in codes])
        cur.execute(
            "INSERT INTO RailStationSource (i, source, name) VALUES (:i, :source, :name_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @property
    def platforms(self) -> Iterator[RailPlatform]:
        """List of :py:class:`RailPlatform` s this stop has"""
        return self._sql_derived("rail/station_platforms", RailPlatform)

    @property
    def connections_from_here(self) -> Iterator[RailConnection]:
        """List of all :py:class:`RailConnection` s departing from this station"""
        return self._sql_derived("rail/station_connections_from_here", RailConnection)

    @property
    def connections_to_here(self) -> Iterator[RailConnection]:
        """List of all :py:class:`RailConnection` s arriving at this station"""
        return self._sql_derived("rail/station_connections_to_here", RailConnection)

    @property
    def lines(self) -> Iterator[RailLine]:
        """List of all :py:class:`RailLine` s at this station"""
        return self._sql_derived("rail/station_lines", RailLine)

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
        self.conn.execute("UPDATE RailPlatform SET station = :i1 WHERE station = :i2", dict(i1=self.i, i2=other.i))
        super()._merge(other)


class RailPlatform(Node):
    code = _Column[str | None]("code", "RailPlatform", formatter=_format_code)
    """Unique code identifying the platform. May not necessarily be the same as the code ingame.
    If ``None``, code is unspecified"""
    station = _FKColumn(RailStation, "station", "RailPlatform")
    """The :py:class:`RailPlatform` of the dock"""
    COLUMNS: ClassVar = (code, station)

    def __str__(self):
        return super().__str__() + f" {self.station.company.name} {'/'.join(self.station.codes)} {self.code}"

    class CreateParams(TypedDict):
        code: str | None
        station: RailStation

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        """Internal use"""
        kwargs = cls.format_create_kwargs(**kwargs)  # pyrefly: ignore[bad-assignment]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO RailPlatform (i, code, station) VALUES (:i, :code, :station)",
            dict(i=i, **kwargs),
        )
        cur.execute("INSERT INTO RailPlatformSource (i, source) VALUES (:i, :source)", dict(i=i, source=src, **kwargs))
        return cls(conn, i)

    @property
    def connections_from_here(self) -> Iterator[RailConnection]:
        """List of all :py:class:`RailConnection` s departing from this platform"""
        return self._sql_derived("rail/berth_connections_from_here", RailConnection)

    @property
    def connections_to_here(self) -> Iterator[RailConnection]:
        """List of all :py:class:`RailConnection` s arriving at this platform"""
        return self._sql_derived("rail/berth_connections_to_here", RailConnection)

    @property
    def lines(self) -> Iterator[RailLine]:
        """List of all :py:class:`RailLine` s at this platform"""
        return self._sql_derived("rail/berth_lines", RailLine)

    def equivalent_nodes(self) -> Iterator[Self]:
        if (code := self.code) is None:
            return iter(())
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM RailPlatform WHERE station = ? AND code = ?", (self.station.i, code)
            ).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute('UPDATE RailConnection SET "from" = :i1 WHERE "from" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute('UPDATE RailConnection SET "to" = :i1 WHERE "to" = :i2', dict(i1=self.i, i2=other.i))


class RailConnection(Node):
    line = _FKColumn(RailLine, "line", "RailConnection")
    """The :py:class:`RailLine` that the connection is made on"""
    from_ = _FKColumn(RailPlatform, "from", "RailConnection")
    """The :py:class:`RailLine` the connection departs from"""
    to = _FKColumn(RailPlatform, "to", "RailConnection")
    """The :py:class:`RailLine` the connection arrives at"""
    direction = _Column[str | None]("direction", "RailConnection", sourced=True, formatter=_format_str)
    """The direction taken when travelling along this connection, e.g. ``Eastbound``, ``towards Terminus Name``"""
    duration = _Column[int | None]("duration", "RailConnection", sourced=True)
    """The duration taken in seconds to travel on this connection"""
    COLUMNS: ClassVar = (line, from_, to, direction, duration)

    def __str__(self):
        return super().__str__() + f" {self.line.company.name} {self.line.code} {self.from_.code} -> {self.to.code}"

    class CreateParams(TypedDict):
        line: RailLine
        from_: RailPlatform
        to: RailPlatform
        direction: NotRequired[str | None]
        duration: NotRequired[int | None]

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        """Internal use"""
        kwargs = cls.format_create_kwargs(**kwargs)  # pyrefly: ignore[bad-assignment]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO RailConnection (i, line, "from", "to", direction, duration) '
            "VALUES (:i, :line, :from_, :to, :direction, :duration)",
            dict(i=i, **kwargs),
        )
        cur.execute(
            "INSERT INTO RailConnectionSource (i, source, direction, duration) "
            "VALUES (:i, :source, :direction_src, :duration_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @classmethod
    def create2(
        cls, conn: sqlite3.Connection, src: int, *, direction2: str | None = None, **kwargs: Unpack[CreateParams]
    ) -> tuple[Self, Self]:
        kwargs2 = kwargs.copy()
        kwargs2["from_"], kwargs2["to"] = kwargs2["to"], kwargs2["from_"]
        kwargs2["direction"] = direction2 or kwargs2["direction"]
        return cls.create(conn, src, **kwargs), cls.create(conn, src, **kwargs2)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT i FROM RailConnection WHERE line = ? AND "from" = ? AND "to" = ?',
                (self.line.i, self.from_.i, self.to.i),
            ).fetchall()
        )
