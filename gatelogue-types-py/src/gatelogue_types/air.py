from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, ClassVar, Literal, NotRequired, Required, Self, TypedDict, Unpack

from gatelogue_types.base import _Column, _FKColumn, _format_code, _format_str, _SetAttr
from gatelogue_types.node import LocatedNode, Node

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Callable, Iterator

type AirMode = Literal["helicopter", "seaplane", "warp plane", "traincarts plane"]


class AirAirline(Node):
    name = _Column[str]("name", "AirAirline", formatter=_format_str)
    """Name of the airline"""
    link = _Column[str | None]("link", "AirAirline", sourced=True, formatter=_format_str)
    """Link to the MRT Wiki page for the airline"""
    COLUMNS: ClassVar = (name, link)

    def __str__(self):
        return super().__str__() + f" {self.name}"

    class CreateParams(TypedDict, total=False):
        name: Required[str]
        link: str | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO AirAirline (i, name, link) VALUES (:i, :name, :link)", dict(i=i, **kwargs))
        cur.execute(
            "INSERT INTO AirAirlineSource (i, source, link) VALUES (:i, :source, :link_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @property
    def flights(self) -> Iterator[AirFlight]:
        """List of all :py:class:`AirFlight` s the airline operates"""
        return (
            AirFlight(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM AirFlight WHERE airline = :i", dict(i=self.i)).fetchall()
        )

    @property
    def gates(self) -> Iterator[AirGate]:
        """List of all :py:class:`AirGate` s the airline owns or operates"""
        return (
            AirGate(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM AirGate WHERE airline = :i", dict(i=self.i)).fetchall()
        )

    @property
    def airports(self) -> Iterator[AirAirport]:
        """List of all :py:class:`AirAirports` s the airline flies to or has gates in"""
        return (
            AirAirport(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT DISTINCT airport FROM AirGate WHERE airline = :i",
                dict(i=self.i),
            ).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM AirAirline WHERE name = ?", (self.name,)).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE AirGate SET airline = :i1 WHERE airline = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE AirFlight SET airline = :i1 WHERE airline = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirAirlineSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirAirline WHERE i = :i2", dict(i1=self.i, i2=other.i))


class AirAirport(LocatedNode):
    @staticmethod
    def _format_airport_code(s: str) -> str:
        s = s.strip().upper()
        if len(s) == 4 and s[3] == "T":
            return s[:3]
        return s

    code = _Column[str]("code", "AirAirport", formatter=_format_airport_code)
    """Unique 3 (sometimes 4)-letter code"""
    names = _SetAttr[str]("AirAirportNames", "name", sourced=True, formatter=_format_str)
    """Name(s) of the airport"""
    link = _Column[str | None]("link", "AirAirport", sourced=True, formatter=_format_str)
    """Link to the MRT Wiki page for the airport"""
    modes = _SetAttr[AirMode]("AirAirportModes", "mode", sourced=True, formatter=_format_str)
    """Types of air vehicle or technology the airport supports"""
    COLUMNS: ClassVar = (*LocatedNode.COLUMNS, code, names, link, modes)

    def __str__(self):
        return super().__str__() + f" {self.code}"

    class CreateParams(LocatedNode.CreateParams, total=False):
        code: Required[str]
        names: set[str]
        link: str | None
        modes: set[AirMode]

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        kwargs = cls.format_create_kwargs(**kwargs)
        names, modes = kwargs.get("names", set()), kwargs.get("modes", set())
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
        cur = conn.cursor()
        cur.execute("INSERT INTO AirAirport (i, code, link) VALUES (:i, :code, :link)", dict(i=i, **kwargs))
        cur.executemany("INSERT INTO AirAirportNames (i, name) VALUES (?, ?)", [(i, name) for name in names])
        cur.executemany("INSERT INTO AirAirportModes (i, mode) VALUES (?, ?)", [(i, mode) for mode in modes])
        cur.execute(
            "INSERT INTO AirAirportSource (i, source, link) VALUES (:i, :source, :link_src)",
            dict(i=i, source=src, **kwargs),
        )
        cur.executemany(
            "INSERT INTO AirAirportNamesSource (i, name, source) VALUES (?, ?, ?)", [(i, name, src) for name in names]
        )
        cur.executemany(
            "INSERT INTO AirAirportModesSource (i, mode, source) VALUES (?, ?, ?)", [(i, mode, src) for mode in modes]
        )
        return cls(conn, i)

    @property
    def gates(self) -> Iterator[AirGate]:
        """List of :py:class:`AirGate` s"""
        return (
            AirGate(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM AirGate WHERE airport = :i", dict(i=self.i)).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        if (code := self.code) == "":
            return iter(())
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM AirAirport WHERE code = ?", (code,)).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE AirGate SET airport = :i1 WHERE airport = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirAirportSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirAirport WHERE i = :i2", dict(i1=self.i, i2=other.i))
        super()._merge(other)


class AirGate(Node):
    code = _Column[str | None]("code", "AirGate", formatter=_format_code)
    """Unique gate code. If ``None``, code is not known"""
    airport = _FKColumn(AirAirport, "airport", "AirGate")
    """The :py:class:`AirAirport`"""
    airline = _FKColumn[AirAirline | None](AirAirline, "airline", "AirGate", sourced=True)
    """The :py:class:`Airline` that owns this gate"""
    size = _Column[str | None]("size", "AirGate", sourced=True, formatter=_format_str)
    """Abbreviated size of the gate (eg. ``S``, ``M``)"""
    mode = _Column[AirMode | None]("mode", "AirGate", sourced=True, formatter=_format_str)
    """Type of air vehicle or technology the gate supports"""
    COLUMNS: ClassVar = (code, airport, airline, size, mode)

    def __str__(self):
        return super().__str__() + f" {self.airport.code} {self.code}"

    class CreateParams(TypedDict, total=False):
        code: Required[str | None]
        airport: Required[AirAirport]
        airline: AirAirline | None
        size: str | None
        mode: AirMode | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO AirGate (i, code, airport, airline, size, mode) VALUES (:i, :code, :airport, :airline, :size, :mode)",
            dict(i=i, **kwargs),
        )
        cur.execute(
            "INSERT INTO AirGateSource (i, source, size, mode, airline) VALUES (:i, :source, :size_src, :mode_src, :airline_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @property
    def flights_from_here(self) -> Iterator[AirFlight]:
        """List of IDs of all :py:class:`AirFlight` s that depart from this gate"""
        return (
            AirFlight(self.conn, i)
            for (i,) in self.conn.execute('SELECT i FROM AirFlight WHERE "from" = :i', dict(i=self.i)).fetchall()
        )

    @property
    def flights_to_here(self) -> Iterator[AirFlight]:
        """List of IDs of all :py:class:`AirFlight` s that arrive at this gate"""
        return (
            AirFlight(self.conn, i)
            for (i,) in self.conn.execute('SELECT i FROM AirFlight WHERE "to" = :i', dict(i=self.i)).fetchall()
        )

    def equivalent_nodes(self) -> Iterator[Self]:
        if (code := self.code) is None:
            return iter(())
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM AirGate WHERE airport = ? AND code = ?", (self.airport.i, code)
            ).fetchall()
        )

    def merge(self, other: Self, warn_fn: Callable[[str], object] = warnings.warn):
        if self.code is None and other.code is not None:
            self.code = other.code
        elif self.code is not None and other.code is None:
            other.code = self.code
        super().merge(other, warn_fn)

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute('UPDATE AirFlight SET "from" = :i1 WHERE "from" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute('UPDATE AirFlight SET "to" = :i1 WHERE "to" = :i2', dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirGateSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirGate WHERE i = :i2", dict(i1=self.i, i2=other.i))


class AirFlight(Node):
    airline = _FKColumn(AirAirline, "airline", "AirFlight")
    """The :py:class:`AirAirline` the flight is operated by"""
    code = _Column[str]("code", "AirFlight", formatter=_format_code)
    """Flight code. May be duplicated if the return flight uses the same code as this flight.
    **2-letter airline prefix not included**"""
    from_ = _FKColumn(AirGate, "from", "AirFlight")
    """The :py:class:`AirGate` this flight departs from"""
    to = _FKColumn(AirGate, "to", "AirFlight")
    """The :py:class:`AirGate` this flight arrives at"""
    mode = _Column[AirMode | None]("mode", "AirFlight", sourced=True, formatter=_format_str)
    """Type of air vehicle or technology used on the flight"""
    COLUMNS: ClassVar = (airline, code, from_, to, mode)

    def __str__(self):
        return super().__str__() + f" {self.airline.name} {self.code}"

    class CreateParams(TypedDict):
        airline: AirAirline
        code: str
        from_: AirGate
        to: AirGate
        mode: NotRequired[AirMode | None]

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
            'INSERT INTO AirFlight (i, "from", "to", code, mode, airline) VALUES (:i, :from_, :to, :code, :mode, :airline)',
            dict(i=i, **kwargs),
        )
        cur.execute(
            "INSERT INTO AirFlightSource (i, source, mode) VALUES (:i, :source, :mode_src)",
            dict(i=i, source=src, **kwargs),
        )
        return cls(conn, i)

    @classmethod
    def create2(
        cls, conn: sqlite3.Connection, src: int, *, code2: str | None = None, **kwargs: Unpack[CreateParams]
    ) -> tuple[Self, Self]:
        kwargs2 = kwargs.copy()
        kwargs2["from_"], kwargs2["to"] = kwargs2["to"], kwargs2["from_"]
        kwargs2["code"] = code2 or kwargs2["code"]
        return cls.create(conn, src, **kwargs), cls.create(conn, src, **kwargs2)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT AirFlight.i FROM AirFlight "
                'LEFT JOIN AirGate AGFrom ON "from" = AGFrom.i '
                'LEFT JOIN AirGate AGTo ON "to" = AGTo.i '
                "WHERE AirFlight.airline = ? AND (AGFrom.airport = ? AND AGTo.airport = ?)",
                (self.airline.i, self.from_.airport.i, self.to.airport.i),
            ).fetchall()
        )

    def merge(self, other: Self, warn_fn: Callable[[str], object] = warnings.warn) -> set[int] | None:
        also_merged = set()
        if (self.from_.code is None or other.from_.code is None) and self.from_ != other.from_:
            also_merged.add(other.from_.i)
            self.from_.merge(other.from_, warn_fn=warn_fn)
        if (self.to.code is None or other.to.code is None) and self.to != other.to:
            also_merged.add(other.to.i)
            self.to.merge(other.to, warn_fn=warn_fn)
        super().merge(other, warn_fn)
        return also_merged

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM AirFlightSource WHERE i = :i2;", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirFlight WHERE i = :i2", dict(i1=self.i, i2=other.i))
