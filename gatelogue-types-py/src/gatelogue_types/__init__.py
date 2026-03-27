"""
Python utility library for using Gatelogue data in Python projects. It will load the database for you to access via ORM or raw SQL.

Installation
------------
Run ``pip install gatelogue-types`` or ``uv add gatelogue-types``. Or add ``gatelogue-types`` to your ``requirements.txt`` or ``pyproject.toml``.

To import directly from the repository, run ``pip install git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-types-py`` or add ``gatelogue-types @ git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-types-py`` to your ``requirements.txt`` or ``pyproject.toml``.

Optionally, you can add an HTTP client (e.g. `requests`, `niquests`) of your choice.

Usage
-----
To retrieve the data:

.. code-block:: python

   import gatelogue_types as gt  # for convenience

   gd = gt.GD.get()  # retrieve data via `urllib` (in standard library)
   gd = gt.GD.get(
       getter=GD.Getters.niquests
   )  # retrieve data with pre-written `niquests` getter
   gd = await gt.GD.get_async(
       getter=GD.Getters.aiohttp
   )  # same but async with pre-written `aiohttp` getter
   gd = await gt.GD.get(
       getter=lambda url: requests.get(url).content
   )  # custom getter. all getters take one `str` and output a `byte`

   # for both .get() and .get_async(), you can make it retrieve a version with sources.
   gd = gt.GD.get(sources=True)

Using the ORM does not require SQL and makes for generally clean code. However, doing this is very inefficient as each attribute access is one SQL query.

.. code-block:: python

   for airport in gd.nodes(gt.AirAirport):
       for gate in airport.gates:
           print(f"Airport {airport.code} has gate {gate.code}")

Querying the underlying SQLite database directly with ``sqlite3`` is generally more efficient and faster. It is also the only way to access the ``*Source`` tables, if you retrieved the database with those.

.. code-block:: python

   for airport_code, gate_code in gd.conn.execute(
       "SELECT A.code, G.code FROM AirGate G INNER JOIN AirAirport A ON G.airport = A.i"
   ).fetchall():
       print(f"Airport {airport.code} has gate {gate.code}")

Note that ``gatelogue-types`` *(py)* is used by ``gatelogue-aggregator``, which is why many classes have methods for modifying the database.
Usage of these methods are discouraged. These are not used in normal use 99% of the time, and they will probably error anyway.

"""

from __future__ import annotations

import datetime
import sqlite3
from typing import (
    TYPE_CHECKING,
    Self,
)

from gatelogue_types.__about__ import __data_version__, __version__
from gatelogue_types._util import _sql
from gatelogue_types.air import AirAirline, AirAirport, Aircraft, AirFlight, AirGate, AirMode
from gatelogue_types.bus import BusBerth, BusCompany, BusConnection, BusLine, BusMode, BusStop
from gatelogue_types.node import LocatedNode, Node, Proximity, SharedFacility, World
from gatelogue_types.rail import (
    RailCompany,
    RailConnection,
    RailLine,
    RailMode,
    RailPlatform,
    RailStation,
)
from gatelogue_types.sea import SeaCompany, SeaConnection, SeaDock, SeaLine, SeaMode, SeaStop
from gatelogue_types.spawn_warp import SpawnWarp, WarpType
from gatelogue_types.town import Rank, Town

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterator
    from os import PathLike

URL: str = "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.db"
URL_NO_SOURCES: str = "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data-ns.db"

__all__ = (
    "GD",
    "AirAirline",
    "AirAirport",
    "AirFlight",
    "AirGate",
    "AirMode",
    "Aircraft",
    "BusBerth",
    "BusCompany",
    "BusConnection",
    "BusLine",
    "BusMode",
    "BusStop",
    "LocatedNode",
    "Node",
    "Proximity",
    "RailCompany",
    "RailConnection",
    "RailLine",
    "RailMode",
    "RailPlatform",
    "RailStation",
    "Rank",
    "SeaCompany",
    "SeaConnection",
    "SeaDock",
    "SeaLine",
    "SeaMode",
    "SeaStop",
    "SharedFacility",
    "SpawnWarp",
    "Town",
    "WarpType",
    "World",
    "__data_version__",
    "__version__",
)


class GD:
    """
    Main class that contains an :py:class:`sqlite3.Connection`
    """

    conn: sqlite3.Connection
    """Connection to the underlying SQL database"""

    def __init__(self, database: str | bytes | PathLike[str] | PathLike[bytes] = ":memory:"):
        sqlite3.threadsafety = 3
        self.conn = sqlite3.connect(database, check_same_thread=False, autocommit=True)
        self.conn.execute("PRAGMA foreign_keys = true")

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        self = cls()
        self.conn.deserialize(data)
        return self

    @classmethod
    def from_bytes_readonly(cls, data: bytes) -> Self:
        self = cls()
        self.conn.deserialize(data)
        self.conn.execute("PRAGMA query_only = true")
        return self

    @classmethod
    def get(cls, *, sources: bool = False, getter: Callable[[str], bytes] | None = None):
        getter = getter or GD.Getters.urllib
        return cls.from_bytes(getter(URL if sources else URL_NO_SOURCES))

    @classmethod
    async def get_async(cls, *, sources: bool = False, getter: Callable[[str], Awaitable[bytes]] | None = None):
        async def _default(url: str):
            return GD.Getters.urllib(url)

        getter = getter or _default
        return cls.from_bytes(await getter(URL if sources else URL_NO_SOURCES))

    class Getters:
        @staticmethod
        def urllib(url: str) -> bytes:
            import urllib.request  # noqa: PLC0415

            if not url.startswith(("http:", "https:")):
                raise ValueError("Invalid URL " + url)
            with urllib.request.urlopen(url) as response:  # noqa: S310
                return response.read()

        @staticmethod
        def niquests(url: str) -> bytes:
            import niquests  # noqa: PLC0415

            return niquests.get(url).content or b""

        @staticmethod
        def requests(url: str) -> bytes:
            import requests  # noqa: PLC0415

            return requests.get(url).content  # noqa: S113

        @staticmethod
        def httpx(url: str) -> bytes:
            import httpx  # noqa: PLC0415

            return httpx.get(url).content

        @staticmethod
        def urllib3(url: str) -> bytes:
            import urllib3  # noqa: PLC0415

            return urllib3.request("GET", url).data

        @staticmethod
        async def rnet(url: str) -> bytes:
            import rnet  # noqa: PLC0415

            return await (await rnet.get(url)).bytes()

        @staticmethod
        async def aiohttp(url: str) -> bytes:
            import aiohttp  # noqa: PLC0415

            session = aiohttp.ClientSession()
            async with (
                session as session,
                session.get(url) as response,
            ):  # pyrefly: ignore [missing-attribute]
                return await response.read()

    @property
    def timestamp(self) -> str:
        """Time that the aggregation of the data was done"""
        return self.conn.execute("SELECT timestamp FROM Metadata").fetchone()[0]

    @property
    def version(self) -> int:
        """Version number of the database format"""
        return self.conn.execute("SELECT version FROM Metadata").fetchone()[0]

    @property
    def has_sources(self) -> bool:
        """Whether the database has sources"""
        return self.conn.execute("SELECT has_sources FROM Metadata").fetchone()[0]

    @classmethod
    def create(cls, sources: list[str], database=":memory:", *, has_sources: bool = True) -> Self:
        """Internal Use"""
        self = cls(database=database)
        cur = self.conn.cursor()
        cur.executescript(_sql("create"))
        cur.execute(
            "INSERT INTO Metadata (version, timestamp, has_sources) VALUES (:version, :timestamp, :has_sources)",
            dict(
                version=__data_version__,
                timestamp=datetime.datetime.now(tz=datetime.UTC).isoformat(),
                has_sources=has_sources,
            ),
        )

        if has_sources:
            cur.executemany("INSERT INTO Source (priority, name) VALUES (?, ?)", list(enumerate(sources)))
        else:
            self.drop_sources(cur)
        self.conn.commit()
        return self

    def drop_sources(self, cur: sqlite3.Cursor | None = None):
        """Drop all ``*Source`` tables"""
        cur = cur or self.conn.cursor()
        cur.executescript(_sql("drop_sources"))

    def get_node[T: Node = Node](self, i: int, ty: type[T] | None = None) -> T:
        """Get a single node

        If ``ty`` is ``None``, :py:class:`LocatedNode` or :py:class:`Node`, find the node type automatically.
        Set ``ty`` to a specific node type only if you can guarantee that the node of ID ``i`` is of said node type."""
        if ty is None or ty is Node:
            return Node.auto_type(self.conn, i)  # pyrefly: ignore[bad-return]
        if ty is LocatedNode:
            return LocatedNode.auto_type(self.conn, i)  # pyrefly: ignore[bad-return]
        return ty(self.conn, i)

    def nodes[T: Node = Node](self, ty: type[T] | None = None) -> Iterator[T]:
        """Get all nodes, optionally of a specific type."""
        if ty is None or ty is Node:
            return (
                Node.STR2TYPE[ty](self.conn, i) for i, ty in self.conn.execute("SELECT i, type FROM Node").fetchall()
            )
        if ty is LocatedNode:
            return (
                Node.STR2TYPE[ty](self.conn, i)
                for i, ty in self.conn.execute(
                    "SELECT NodeLocation.i, type FROM NodeLocation LEFT JOIN Node on Node.i = NodeLocation.i"
                ).fetchall()
            )
        return (
            ty(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM Node WHERE type = :type", dict(type=ty.__name__))
        )

    def __iter__(self) -> Iterator[Node]:
        return self.nodes()

    def __len__(self):
        return self.conn.execute("SELECT count(rowid) FROM Node").fetchone()[0]
