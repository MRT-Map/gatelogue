from __future__ import annotations

import contextlib
import datetime
import sqlite3
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Self,
)

from gatelogue_types.__about__ import __data_version__
from gatelogue_types.air import AirAirline, AirAirport, AirFlight, AirGate, AirMode
from gatelogue_types.bus import BusBerth, BusCompany, BusConnection, BusLine, BusMode, BusStop
from gatelogue_types.node import LocatedNode, Node, Proximity, SharedFacility, World
from gatelogue_types.rail import RailCompany, RailConnection, RailLine, RailMode, RailPlatform, RailStation
from gatelogue_types.sea import SeaCompany, SeaConnection, SeaDock, SeaLine, SeaMode, SeaStop
from gatelogue_types.spawn_warp import SpawnWarp, WarpType
from gatelogue_types.town import Rank, Town

if TYPE_CHECKING:
    # pyrefly: ignore [missing-import]
    from collections.abc import Iterator

    import aiohttp

URL: str = "???"
URL_NO_SOURCES: str = "???"

class GD:
    conn: sqlite3.Connection

    def __init__(self, database=":memory:"):
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
    def niquests_get(cls, sources: bool = False, *args, **kwargs):
        # pyrefly: ignore [missing-import]
        import niquests

        return cls.from_bytes_readonly(niquests.get(URL if sources else URL_NO_SOURCES, *args, **kwargs).content)

    @classmethod
    def requests_get(cls, sources: bool = False, *args, **kwargs):
        # pyrefly: ignore [missing-import,missing-source-for-stubs]
        import requests

        return cls.from_bytes_readonly(requests.get(URL if sources else URL_NO_SOURCES, *args, **kwargs).content)

    @classmethod
    def httpx_get(cls, sources: bool = False, *args, **kwargs):
        # pyrefly: ignore [missing-import]
        import httpx

        return cls.from_bytes_readonly(httpx.get(URL if sources else URL_NO_SOURCES, *args, **kwargs).content)

    @classmethod
    def urllib3_get(cls, sources: bool = False, *args, **kwargs):
        # pyrefly: ignore [missing-import]
        import urllib3

        return cls.from_bytes_readonly(urllib3.request("GET", URL if sources else URL_NO_SOURCES, *args, **kwargs).data)

    @classmethod
    def urllib_get(cls, sources: bool = False, *args, **kwargs):
        import urllib.request

        with urllib.request.urlopen(URL if sources else URL_NO_SOURCES, *args, **kwargs) as response:  # noqa: S310
            return cls.from_bytes_readonly(response.read())

    @classmethod
    async def aiohttp_get(cls, sources: bool = False, session: aiohttp.ClientSession | None = None) -> Self:
        # pyrefly: ignore [missing-import]
        import aiohttp

        session = aiohttp.ClientSession() if session is None else contextlib.nullcontext(session)
        async with session as session, session.get(URL if sources else URL_NO_SOURCES) as response:  # pyrefly: ignore [missing-attribute]
            return cls.from_bytes_readonly(await response.read())

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
    def create(cls, sources: list[str], database=":memory:", has_sources: bool = True) -> Self:
        """Create a new Gatelogue database"""
        self = cls(database=database)
        cur = self.conn.cursor()
        cur.executescript((Path(__file__).parent / "create.sql").read_text())
        cur.execute(
            "INSERT INTO Metadata (version, timestamp, has_sources) VALUES (:version, :timestamp, :has_sources)",
            dict(version=__data_version__, timestamp=datetime.datetime.now().isoformat(), has_sources=has_sources),
        )

        if has_sources:
            cur.executemany("INSERT INTO Source (priority, name) VALUES (?, ?)", list(enumerate(sources)))
        else:
            self.drop_sources(cur)
        self.conn.commit()
        return self

    def drop_sources(self, cur: sqlite3.Cursor | None = None):
        cur = cur or self.conn.cursor()
        cur.executescript((Path(__file__).parent / "drop_sources.sql").read_text())

    def get_node[T: Node = Node](self, i: int, ty: type[T] | None = None) -> T:
        if ty is None or ty is Node:
            return Node.auto_type(self.conn, i)
        if ty is LocatedNode:
            return LocatedNode.auto_type(self.conn, i)
        return ty(self.conn, i)

    def nodes[T: Node = Node](self, ty: type[T] | None = None) -> Iterator[T]:
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
