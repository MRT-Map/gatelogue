from __future__ import annotations

import contextlib
import datetime
import sqlite3
import warnings
from collections.abc import Iterable, Iterator, Callable
from pathlib import Path
from typing import TYPE_CHECKING, Literal, LiteralString, ParamSpec, Self, ClassVar, overload, TypedDict, Required, Unpack, \
    NotRequired

from gatelogue_types.__about__ import __data_version__

if TYPE_CHECKING:
    # pyrefly: ignore [missing-import]
    import aiohttp

URL: str = "???"

class GD:
    def __init__(self, database=":memory:"):
        sqlite3.threadsafety = 3
        self.conn = sqlite3.connect(database, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = true")

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        self = cls()
        self.conn.deserialize(data)
        return self

    @classmethod
    def niquests_get(cls, *args, **kwargs):
        # pyrefly: ignore [missing-import]
        import niquests
        return cls.from_bytes(niquests.get(URL, *args, **kwargs).content)

    @classmethod
    def requests_get(cls, *args, **kwargs):
        # pyrefly: ignore [missing-import,missing-source-for-stubs]
        import requests

        return cls.from_bytes(requests.get(URL, *args, **kwargs).content)

    @classmethod
    def httpx_get(cls, *args, **kwargs):
        # pyrefly: ignore [missing-import]
        import httpx

        return cls.from_bytes(httpx.get(URL, *args, **kwargs).bytes)

    @classmethod
    def urllib3_get(cls, *args, **kwargs):
        # pyrefly: ignore [missing-import]
        import urllib3

        return cls.from_bytes(urllib3.request("GET", URL, *args, **kwargs).data)

    @classmethod
    def urllib_get(cls, *args, **kwargs):
        import urllib.request

        with urllib.request.urlopen(URL, *args, **kwargs) as response:  # noqa: S310
            return cls.from_bytes(response.read())

    @classmethod
    async def aiohttp_get(cls, session: aiohttp.ClientSession | None = None) -> Self:
        # pyrefly: ignore [missing-import]
        import aiohttp

        session = aiohttp.ClientSession() if session is None else contextlib.nullcontext(session)
        async with session as session, session.get(URL) as response:  # pyrefly: ignore [missing-attribute]
            return cls.from_bytes(response.bytes())

    @property
    def timestamp(self):
        """Time that the aggregation of the data was done"""
        return self.conn.execute("SELECT timestamp FROM Metadata").fetchone()[0]

    @property
    def version(self):
        """Version number of the database format"""
        return self.conn.execute("SELECT version FROM Metadata").fetchone()[0]

    @classmethod
    def create(cls, sources: list[str], database=":memory:") -> Self:
        """Create a new Gatelogue database"""
        self = cls(database=database)
        cur = self.conn.cursor()
        with open(Path(__file__).parent / "create.sql") as f:
            cur.executescript(f.read())
        cur.executemany("INSERT INTO Source (priority, name) VALUES (?, ?)", list(enumerate(sources)))
        cur.execute(
            "INSERT INTO Metadata (version, timestamp) VALUES (:version, :timestamp)",
            dict(version=__data_version__, timestamp=datetime.datetime.now().isoformat()),
        )
        self.conn.commit()
        return self

    def get_node[T: Node = Node](self, i: int, ty: type[T] | None = None) -> T:
        if ty is None:
            ty = Node._STR2TYPE[self.conn.execute("SELECT type FROM Node WHERE i = :i", dict(i=i)).fetchone()[0]]
        return ty(self.conn, i)

    @overload
    def nodes(self) -> Iterator[Node]:
        ...

    @overload
    def nodes[T: Node](self, ty: type[T]) -> Iterator[T]:
        ...

    def nodes[T: Node = Node](self, ty: type[T] | None = None) -> Iterator[T]:
        if ty is None:
            return (Node._STR2TYPE[ty](self.conn, i) for i, ty in self.conn.execute("SELECT i, type FROM Node").fetchall())
        return (ty(self.conn, i) for i, in self.conn.execute("SELECT i FROM Node WHERE type = :type", dict(type=ty.__name__)))

    def __iter__(self) -> Iterator[Node]:
        return self.nodes()

    def __len__(self):
        return self.conn.execute("SELECT count(rowid) FROM Node").fetchone()[0]


class _Column[T]:
    def __init__(self, name: LiteralString, table: LiteralString, sourced: bool = False):
        self.name = f'"{name}"'
        self.table = table
        self.sourced = sourced

    def __get__(self, instance: Node, owner: type[Node]) -> T:
        return instance.conn.execute(
            f"SELECT {self.name} FROM {self.table} WHERE i = :i", dict(i=instance.i)
        ).fetchone()[0]

    def __set__(self, instance: Node, value: T | tuple[set[int], T]):
        srcs, value = value if isinstance(value, tuple) else (instance.sources, value)
        cur = instance.conn.cursor()
        cur.execute(f"UPDATE {self.table} SET {self.name} = :value WHERE i = :i", dict(value=value, i=instance.i))
        if not self.sourced:
            return
        for src in srcs:
            cur.execute(
                f"INSERT INTO {self.table + 'Source'} (i, source, {self.name}) VALUES (:i, :source, :bool) ON CONFLICT (i, source) DO UPDATE SET {self.name} = :bool",
                dict(bool=value is not None, i=instance.i, source=src),
            )

    def sources(self, instance: Node) -> set[int]:
        return {
            src
            for (src,) in instance.conn.execute(
                f"SELECT DISTINCT source FROM {self.table + 'Source'} WHERE {self.name} = true"
            ).fetchall()
        }

    def _merge(self, instance1: Node, instance2: Node, warn_fn: Callable[[str]]):
        self_v = self.__get__(instance1, type(instance1))
        other_v = self.__get__(instance2, type(instance2))
        if not self.sourced:
            if self_v != other_v:
                self_sources = instance1.sources
                other_sources = instance2.sources
                if min(self_sources) >= min(other_sources):
                    warn_fn(f"Column {self.name} in table {self.table} is different between {instance1} ({self_v}) and {instance2} ({other_v}). Former has higher priority of {self_sources} than latter which has {other_sources}")
                else:
                    warn_fn(f"Column {self.name} in table {self.table} is different between {instance1} ({self_v}) and {instance2} ({other_v}). Latter has higher priority of {self_sources} than former which has {other_sources}")
                    self.__set__(instance1, other_v)
            return
        match (self_v, other_v):
            case (None, None):
                pass
            case (_, None):
                pass
            case (None, _):
                sources = self.sources(instance2)
                self.__set__(instance1, (sources, other_v))
            case (_, _) if self_v != other_v:
                # TODO warning for override
                self_sources = self.sources(instance1)
                other_sources = self.sources(instance2)
                if min(self_sources) >= min(other_sources):
                    warn_fn(f"Column {self.name} in table {self.table} is different between {instance1} ({self_v}) and {instance2} ({other_v}). Former has higher priority of {self_sources} than latter which has {other_sources}")
                    self.__set__(instance2, None)
                else:
                    warn_fn(f"Column {self.name} in table {self.table} is different between {instance1} ({self_v}) and {instance2} ({other_v}). Latter has higher priority of {self_sources} than former which has {other_sources}")
                    self.__set__(instance1, (other_sources, other_v))


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

    def __set__(self, instance: Node, value: T | tuple[int, T]):
        _Column(self.name, self.table, self.sourced).__set__(instance, None if value is None else value.i)

    def _merge(self, instance1: Node, instance2: Node, warn_fn: Callable[[str]]):
        _Column(self.name, self.table, self.sourced)._merge(instance1, instance2, warn_fn)


class _SetAttr[T]:
    def __init__(self, table: LiteralString, table_column: LiteralString, sourced: bool = False):
        self.table = table
        self.table_column = table_column
        self.sourced = sourced

    def __get__(self, instance: Node, owner: type[Node]) -> set[T]:
        return {
            v
            for (v,) in instance.conn.execute(
                f"SELECT {self.table_column} FROM {self.table} WHERE i = :i", dict(i=instance.i)
            ).fetchall()
        }

    def __set__(self, instance: Node, values: set[T] | tuple[set[int], set[T]]):
        srcs, values = values if isinstance(values, tuple) else (instance.sources, values)
        cur = instance.conn.cursor()
        if not self.sourced:
            cur.execute(f"DELETE FROM {self.table} WHERE i = :i", dict(i=instance.i))
            cur.executemany(
                f"INSERT INTO {self.table} (i, {self.table_column}) VALUES (:i, :value)",
                [dict(i=instance.i, value=value) for value in values],
            )
            return
        existing_values = {
            v
            for (v,) in cur.execute(
                f"SELECT {self.table_column} FROM {self.table + 'Source'} WHERE i = :i AND source IN :sources",
                dict(i=instance.i, sources=srcs),
            ).fetchall()
        }
        for new_value in values - existing_values:
            cur.execute(
                f"INSERT INTO {self.table} (i, {self.table_column}) VALUES (:i, :value) "
                f"ON CONFLICT (i, {self.table_column}) DO NOTHING",
                dict(i=instance.i, value=new_value),
            )
            cur.executemany(
                f"INSERT INTO {self.table + 'Source'} (i, {self.table_column}, source) VALUES (:i, :value, :source) "
                f"ON CONFLICT (i, {self.table_column}) DO NOTHING",
                [dict(i=instance.i, value=new_value, source=src) for src in srcs],
            )
        for old_value in existing_values - values:
            cur.execute(
                f"DELETE FROM {self.table + 'Source'} WHERE i = :i AND {self.table_column} = :value AND source IN :sources",
                dict(i=instance.i, value=old_value, sources=srcs),
            )
            if (
                cur.execute(
                    f"SELECT count(i) FROM {self.table + 'Source'} WHERE i = :i AND {self.table_column} = :value",
                    dict(i=instance.i, value=old_value),
                ).fetchone()[0]
                == 0
            ):
                cur.execute(
                    f"DELETE FROM {self.table} WHERE i = :i AND {self.table_column} = :value",
                    dict(i=instance.i, value=old_value),
                )

    def _merge(self, instance1: Node, instance2: Node):
        cur = instance1.conn.cursor()
        cur.execute(
            f"INSERT INTO {self.table} (i, {self.table_column}) "
            f"SELECT :i1, {self.table_column} FROM {self.table} WHERE i = :i2 "
            f"ON CONFLICT (i, {self.table_column}) DO NOTHING",
            dict(i1=instance1.i, i2=instance2.i),
        )
        if self.sourced:
            cur.execute(
                f"UPDATE OR FAIL {self.table + 'Source'} SET i = :i1 WHERE i = :i2",
                dict(i1=instance1.i, i2=instance2.i),
            )
        cur.execute(f"DELETE FROM {self.table} WHERE i = :i2", dict(i1=instance1.i, i2=instance2.i))


type World = Literal["New", "Old", "Space"]
type AirMode = Literal["helicopter", "seaplane", "warp plane", "traincarts plane"]
type BusMode = Literal["warp", "traincarts"]
type SeaMode = Literal["cruise", "warp ferry", "traincarts ferry"]
type RailMode = Literal["warp", "cart", "traincarts", "vehicles"]
type WarpType = Literal["premier", "terminus", "traincarts", "portal", "misc"]
type Rank = Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]


class Node:
    _STR2TYPE: ClassVar[dict] = {}
    def __init_subclass__(cls, **kwargs):
        cls._STR2TYPE[cls.__name__] = cls

    def __init__(self, conn: sqlite3.Connection, i: int):
        self.conn = conn
        self.i = i
        """The ID of the node"""


    type = _Column[str]("type", "Node")
    """The type of the node"""
    sources = _SetAttr[int]("NodeSource", "source")
    """All sources that prove the node's existence"""

    @property
    def source(self) -> int:
        sources = self.sources
        assert len(sources) == 1, "Expected only one source"
        return next(iter(sources))

    @source.setter
    def source(self, value: int):
        self.sources = {value}

    @classmethod
    def create_node(cls, conn: sqlite3.Connection, src: int, *, ty: str) -> int:
        cur = conn.cursor()
        cur.execute("INSERT INTO Node ( type ) VALUES ( :type )", dict(type=ty))
        (i,) = cur.execute("SELECT i FROM Node WHERE ROWID = :rowid", dict(rowid=cur.lastrowid)).fetchone()
        cur.execute("INSERT INTO NodeSource ( i, source ) VALUES ( :i, :source )", dict(i=i, source=src))
        return i

    def __eq__(self, other: Self) -> bool:
        return self.i == other.i

    def equivalent_nodes(self) -> Iterator[Self]:
        raise NotImplementedError

    def _merge(self, other: Self):
        raise NotImplementedError

    def merge(self, other: Self, warn_fn: Callable[[str]] = warnings.warn):
        for name, attr in type(self).__dict__.items():
            if isinstance(attr, (_Column, _FKColumn, _SetAttr)):
                attr._merge(self, other, warn_fn)

        self._merge(other)

        cur = self.conn.cursor()
        cur.execute("DELETE FROM NodeSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM Node WHERE i = :i2", dict(i1=self.i, i2=other.i))


class LocatedNode(Node):
    world = _Column[str | None]("world", "LocatedNode", sourced=True)
    """The world the node is in"""
    _x = _Column[int | None]("x", "LocatedNode", sourced=True)
    """The x-coordinate of the node"""
    _y = _Column[int | None]("y", "LocatedNode", sourced=True)
    """The y-coordinate of the node"""

    @property
    def coordinates(self) -> tuple[int, int] | None:
        """The coordinates of the object"""
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

    class CreateParams(TypedDict, total=False):
        world: World | None
        coordinates: tuple[int, int] | None

    @classmethod
    def create_node_with_location(
        cls,
        conn: sqlite3.Connection,
        src: int,
        *,
        ty: str,
        **kwargs: Unpack[CreateParams]
    ) -> int:
        world, coordinates = kwargs.get("world", None), kwargs.get("coordinates", None)
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

    @property
    def nodes_in_proximity(self) -> Iterator[tuple[LocatedNode, Proximity]]:
        """
        References all nodes that are near (within walking distance of) this object.

        :return: Pairs of nodes in proximity as well as proximity data (:py:class:`Proximity`).
        """
        return (
            (LocatedNode(self.conn, j if self.i == i else i), Proximity(self.conn, i, j))
            for i, j in self.conn.execute(
                "SELECT node1, node2 FROM Proximity WHERE node1 = :i OR node2 = :i", dict(i=self.i)
            ).fetchall()
        )

    @property
    def shared_facility(self) -> Iterable[LocatedNode]:
        """References all nodes that this object shares the same facility with (same building, station, hub etc)"""
        return (
            LocatedNode(self.conn, j if self.i == i else i)
            for i, j in self.conn.execute(
                "SELECT node1, node2 FROM Proximity WHERE node1 = :i OR node2 = :i", dict(i=self.i)
            ).fetchall()
        )

    def _merge(self, other: Self):
        # TODO handle merging of Proximity
        cur = self.conn.cursor()
        cur.execute("UPDATE OR FAIL SharedFacility SET node1 = :i1 WHERE node1 = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE OR FAIL SharedFacility SET node2 = :i1 WHERE node2 = :i2", dict(i1=self.i, i2=other.i))
        cur.execute(
            "INSERT INTO Proximity SELECT :i1, node2, distance, explicit FROM Proximity "
            "WHERE node1 = :i2 ON CONFLICT (node1, node2) DO NOTHING",
            dict(i1=self.i, i2=other.i),
        )
        cur.execute(
            "INSERT INTO Proximity SELECT node1, :i1, distance, explicit FROM Proximity "
            "WHERE node2 = :i2 ON CONFLICT (node1, node2) DO NOTHING",
            dict(i1=self.i, i2=other.i),
        )
        cur.execute("UPDATE OR FAIL ProximitySource SET node1 = :i1 WHERE node1 = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE OR FAIL ProximitySource SET node2 = :i1 WHERE node2 = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM Proximity WHERE node1 == :i2 OR node2 == :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM NodeLocationSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM NodeLocation WHERE i = :i2", dict(i1=self.i, i2=other.i))


class Proximity:
    def __init__(self, conn: sqlite3.Connection, node1: LocatedNode, node2: LocatedNode):
        self.conn = conn
        if node1.i > node2.i:
            node1, node2 = node2, node1
        self.node1 = node1.i
        self.node2 = node2.i

    @property
    def distance(self):
        """Distance between the two objects in blocks"""
        return self.conn.execute(
            "SELECT distance from Proximity WHERE node1 = :node1 AND node2 = :node2",
            dict(node1=self.node1, node2=self.node2),
        ).fetchone()[0]

    @distance.setter
    def distance(self, value: float):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE Proximity set distance = :value WHERE node1 = :node1 AND node2 = :node2",
            dict(value=value, node1=self.node1, node2=self.node2),
        )

    @property
    def explicit(self):
        """Whether this relation is explicitly recognised by the company/ies of the stations. Used mostly for local services"""
        return self.conn.execute(
            "SELECT explicit from Proximity WHERE node1 = :node1 AND node2 = :node2",
            dict(node1=self.node1, node2=self.node2),
        ).fetchone()[0]

    @explicit.setter
    def explicit(self, value: bool):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE Proximity set explicit = :value WHERE node1 = :node1 AND node2 = :node2",
            dict(value=value, node1=self.node1, node2=self.node2),
        )

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        srcs: Iterable[int],
        *,
        node1: LocatedNode,
        node2: LocatedNode,
        distance: float,
        explicit: bool = False,
    ) -> Self:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Proximity (node1, node2, distance, explicit) VALUES (:node1, :node2, :distance, :explicit)",
            dict(node1=node1.i, node2=node2.i, distance=distance, explicit=explicit),
        )
        cur.execute(
            "INSERT INTO ProximitySource ( node1, node2, source ) VALUES ( :node1, :node2, :source )",
            [dict(node1=node1.i, node2=node2.i, source=src) for src in srcs],
        )
        return cls(conn, node1, node2)


class SharedFacility:
    def __init__(self, conn: sqlite3.Connection, node1: LocatedNode, node2: LocatedNode):
        self.conn = conn
        if node1.i > node2.i:
            node1, node2 = node2, node1
        self.node1 = node1.i
        self.node2 = node2.i

    @classmethod
    def create(cls, conn: sqlite3.Connection, *, node1: LocatedNode, node2: LocatedNode) -> Self:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO SharedFacility (node1, node2) VALUES (:node1, :node2)", dict(node1=node1.i, node2=node2.i)
        )
        return cls(conn, node1, node2)


class AirAirline(Node):
    name = _Column[str]("name", "AirAirline")
    """Name of the airline"""
    link = _Column[str | None]("link", "AirAirline", sourced=True)
    """Link to the MRT Wiki page for the airline"""

    class CreateParams(TypedDict, total=False):
        name: Required[str]
        link: str | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        name, link = kwargs["name"], kwargs.get("link", None)
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
    code = _Column[str]("code", "AirAirport")
    """Unique 3 (sometimes 4)-letter code"""
    names = _SetAttr[str]("AirAirportNames", "name", sourced=True)
    """Name(s) of the airport"""
    link = _Column[str | None]("link", "AirAirport", sourced=True)
    """Link to the MRT Wiki page for the airport"""
    modes = _SetAttr[AirMode]("AirAirportModes", "mode", sourced=True)
    """Types of air vehicle or technology the airport supports"""

    class CreateParams(LocatedNode.CreateParams, total=False):
        code: Required[str]
        names: set[str]
        link: str | None
        modes: set[AirMode]

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        **kwargs: Unpack[CreateParams]
    ) -> Self:
        code, names, link, modes = kwargs["code"], kwargs.get("names", set()), kwargs.get("link", None), kwargs.get("modes", set())
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
        cur = conn.cursor()
        cur.execute("INSERT INTO AirAirport (i, code, link) VALUES (:i, :code, :link)", dict(i=i, code=code, link=link))
        cur.executemany("INSERT INTO AirAirportNames (i, name) VALUES (?, ?)", [(i, name) for name in names])
        cur.executemany("INSERT INTO AirAirportModes (i, mode) VALUES (?, ?)", [(i, mode) for mode in modes])
        cur.execute(
            "INSERT INTO AirAirportSource (i, source, link) VALUES (:i, :source, :link)",
            dict(i=i, source=src, link=link is not None),
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
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM AirAirport WHERE code = ?", (self.code,)).fetchall()
        )

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE AirGate SET airport = :i1 WHERE airport = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirAirportSource WHERE i = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirAirport WHERE i = :i2", dict(i1=self.i, i2=other.i))
        super()._merge(other)


class AirGate(Node):
    code = _Column[str | None]("code", "AirGate")
    """Unique gate code. If ``None``, code is not known"""
    airport = _FKColumn(AirAirport, "airport", "AirGate")
    """The :py:class:`AirAirport`"""
    airline = _FKColumn[AirAirline | None](AirAirline, "airline", "AirGate", sourced=True)
    """The :py:class:`Airline` that owns this gate"""
    size = _Column[str | None]("size", "AirGate", sourced=True)
    """Abbreviated size of the gate (eg. ``S``, ``M``)"""
    mode = _Column[AirMode | None]("mode", "AirGate", sourced=True)
    """Type of air vehicle or technology the gate supports"""

    class CreateParams(TypedDict, total=False):
        code: Required[str | None]
        airport: Required[AirAirport]
        airline: AirAirline | None
        size: str | None
        mode: AirMode | None

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        **kwargs: Unpack[CreateParams]
    ) -> Self:
        code, airport, airline, size, mode = kwargs["code"], kwargs["airport"], kwargs.get("airline", None), kwargs.get("size", None), kwargs.get("mode", None)
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

    def merge(self, other: Self, warn_fn: Callable[[str]] = warnings.warn):
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
    code = _Column[str]("code", "AirFlight")
    """Flight code. May be duplicated if the return flight uses the same code as this flight.
    **2-letter airline prefix not included**"""
    from_ = _FKColumn(AirGate, "from", "AirFlight")
    """The :py:class:`AirGate` this flight departs from"""
    to = _FKColumn(AirGate, "to", "AirFlight")
    """The :py:class:`AirGate` this flight arrives at"""
    mode = _Column[str | None]("mode", "AirFlight", sourced=True)
    """Type of air vehicle or technology used on the flight"""

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
        airline, code, from_, to, mode = kwargs["airline"], kwargs["code"], kwargs["from_"], kwargs["to"], kwargs.get("mode", None)
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

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                'SELECT AirFlight.i FROM AirFlight '
                'LEFT JOIN AirGate AGFrom ON "from" = AGFrom.i '
                'LEFT JOIN AirGate AGTo ON "to" = AGTo.i '
                'WHERE AirFlight.airline = ? AND (AirFlight.code = ? OR (AGFrom.airport = ? AND AGTo.airport = ?))',
                (self.airline.i, self.code, self.from_.airport.i, self.to.airport.i),
            ).fetchall()
        )

    def merge(self, other: Self, warn_fn: Callable[[str]] = warnings.warn):
        if self.from_.code is None or other.from_.code is None:
            self.from_.merge(other.from_)
        if self.to.code is None or other.to.code is None:
            self.to.merge(other.to)
        super().merge(other, warn_fn)

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM AirFlightSource WHERE i = :i2;", dict(i1=self.i, i2=other.i))
        cur.execute("DELETE FROM AirFlight WHERE i = :i2", dict(i1=self.i, i2=other.i))


class BusCompany(Node):
    name = _Column[str]("name", "BusCompany")
    """Name of the bus company"""

    class CreateParams(TypedDict):
        name: str

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        name = kwargs["name"]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO BusCompany (i, name) VALUES (:i, :name)", dict(i=i, name=name))
        cur.execute("INSERT INTO BusCompanySource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
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
    code = _Column[str]("code", "BusLine")
    """Unique code identifying the bus line"""
    company = _FKColumn(BusCompany, "company", "BusLine")
    """The :py:class:`BusCompany` that operates the line"""
    name = _Column[str | None]("name", "BusLine", sourced=True)
    """Name of the line"""
    colour = _Column[str | None]("colour", "BusLine", sourced=True)
    """Colour of the line (on a map)"""
    mode = _Column[str | None]("mode", "BusLine", sourced=True)
    """Type of bus vehicle or technology the line uses"""
    local = _Column[bool | None]("name", "BusLine", sourced=True)
    """Whether the line operates within the city, e.g. a local bus service"""

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
        code, company, name, colour, mode, local = kwargs["code"], kwargs["company"], kwargs.get("name", None), kwargs.get("colour", None), kwargs.get("mode", None), kwargs.get("local", None)
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
    codes = _SetAttr[str]("BusStopCodes", "code")
    """Unique code(s) identifying the bus stop. May also be the same as the name"""
    company = _FKColumn(BusCompany, "company", "BusStop")
    """The :py:class:`BusCompany` that owns this stop"""
    name = _Column[str | None]("name", "BusStop", sourced=True)
    """Name of the stop"""

    class CreateParams(LocatedNode.CreateParams, total=False):
        codes: Required[set[str]]
        company: Required[BusCompany]
        name: str | None

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        **kwargs: Unpack[CreateParams]
    ) -> Self:
        codes, company, name = kwargs["codes"], kwargs["company"], kwargs.get("name", None)
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
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
    code = _Column[str | None]("code", "BusBerth")
    """Unique code identifying the berth. May not necessarily be the same as the code ingame. If ``None``, code is unspecified"""
    stop = _FKColumn(BusStop, "stop", "BusStop")
    """The :py:class:`BusStop` of the berth"""

    class CreateParams(TypedDict):
        code: str | None
        stop: BusStop

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        **kwargs: Unpack[CreateParams]
    ) -> Self:
        code, stop = kwargs["code"], kwargs["stop"]
        i = cls.create_node(conn, src, ty=cls.__name__)
        cur = conn.cursor()
        cur.execute("INSERT INTO BusBerth (i, code, stop) VALUES (:i, :code, :stop)", dict(i=i, code=code, stop=stop.i))
        cur.execute("INSERT INTO BusBerthSource (i, source) VALUES (:i, :source)", dict(i=i, source=src))
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
    direction = _Column[str | None]("direction", "BusConnection", sourced=True)
    """The direction taken when travelling along this connection, e.g. ``Eastbound``, ``towards Terminus Name``"""

    class CreateParams(TypedDict):
        line: BusLine
        from_: BusBerth
        to: BusBerth
        direction: NotRequired[str | None]

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        **kwargs: Unpack[CreateParams]
    ) -> Self:
        line, from_, to, direction = kwargs["line"], kwargs["from_"], kwargs["to"], kwargs.get("direction", None)
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
        code, company, name, colour, mode, local = kwargs["code"], kwargs["company"], kwargs.get("name", None), kwargs.get("colour", None), kwargs.get("mode", None), kwargs.get("local", None)
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
    def create(
            cls,
            conn: sqlite3.Connection,
            src: int,
            **kwargs: Unpack[CreateParams]
    ) -> Self:
        codes, company, name = kwargs["codes"], kwargs["company"], kwargs.get("name", None)
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
    def create(
            cls,
            conn: sqlite3.Connection,
            src: int,
            **kwargs: Unpack[CreateParams]
    ) -> Self:
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
    def create(
            cls,
            conn: sqlite3.Connection,
            src: int,
            **kwargs: Unpack[CreateParams]
    ) -> Self:
        line, from_, to, direction = kwargs["line"], kwargs["from_"], kwargs["to"], kwargs.get("direction", None)
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
        code, company, name, colour, mode, local = kwargs["code"], kwargs["company"], kwargs.get("name", None), kwargs.get("colour", None), kwargs.get("mode", None), kwargs.get("local", None)
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
    def create(
            cls,
            conn: sqlite3.Connection,
            src: int,
            **kwargs: Unpack[CreateParams]
    ) -> Self:
        codes, company, name = kwargs["codes"], kwargs["company"], kwargs.get("name", None)
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
        stop: RailStation

    @classmethod
    def create(
            cls,
            conn: sqlite3.Connection,
            src: int,
            **kwargs: Unpack[CreateParams]
    ) -> Self:
        code, stop = kwargs["code"], kwargs["stop"]
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
    def create(
            cls,
            conn: sqlite3.Connection,
            src: int,
            **kwargs: Unpack[CreateParams]
    ) -> Self:
        line, from_, to, direction = kwargs["line"], kwargs["from_"], kwargs["to"], kwargs.get("direction", None)
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


class SpawnWarp(LocatedNode):
    name = _Column[str]("name", "SpawnWarp")
    """Name of the spawn warp"""
    warp_type = _Column[str]("warpType", "SpawnWarp")
    """The type of the spawn warp"""

    class CreateParams(LocatedNode.CreateParams, total=True):
        name: str
        warp_type: str

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        **kwargs: Unpack[CreateParams],
    ) -> Self:
        name, warp_type = kwargs["name"], kwargs["warp_type"]
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO SpawnWarp (i, name, warpType) VALUES (:i, :name, :warp_type)",
            dict(i=i, name=name, warp_type=warp_type),
        )
        return cls(conn, i)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM SpawnWarp WHERE name = ? and warpType = ?", (self.name, self.warp_type)
            ).fetchall()
        )

    def _merge(self, other: Self):
        self.conn.execute("DELETE FROM SpawnWarp WHERE i = :i2", dict(i1=self.i, i2=other.i))
        super()._merge(other)


class Town(LocatedNode):
    name = _Column[str]("name", "Town")
    """Name of the town"""
    rank = _Column[str]("rank", "Town")
    """Rank of the town"""
    mayor = _Column[str]("mayor", "Town")
    """Mayor of the town"""
    deputy_mayor = _Column[str | None]("deputyMayor", "Town")
    """Deputy Mayor of the town"""

    class CreateParams(LocatedNode.CreateParams, total=True):
        name: str
        rank: str
        mayor: str
        deputy_mayor: str | None

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        src: int,
        **kwargs: Unpack[CreateParams]
    ) -> Self:
        name, rank, mayor, deputy_mayor = kwargs["name"], kwargs["rank"], kwargs["mayor"], kwargs["deputy_mayor"]
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Town (i, name, rank, mayor, deputyMayor) VALUES (:i, :name, :rank, :mayor, :deputy_mayor)",
            dict(i=i, name=name, rank=rank, mayor=mayor, deputy_mayor=deputy_mayor),
        )
        return cls(conn, i)

    def equivalent_nodes(self) -> Iterator[Self]:
        return (
            type(self)(self.conn, i)
            for (i,) in self.conn.execute(
                "SELECT i FROM Town WHERE name = ? and mayor = ?", (self.name, self.mayor)
            ).fetchall()
        )

    def _merge(self, other: Self):
        self.conn.execute("DELETE FROM SpawnWarp WHERE i = :i2", dict(i1=self.i, i2=other.i))
        super()._merge(other)
