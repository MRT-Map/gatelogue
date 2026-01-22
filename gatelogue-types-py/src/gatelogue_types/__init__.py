__all__ = ()

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
from gatelogue_types.node import Node, LocatedNode, Proximity, SharedFacility
from gatelogue_types.air import AirAirline, AirAirport, AirGate, AirFlight
from gatelogue_types.bus import BusCompany, BusLine, BusStop, BusBerth, BusConnection
from gatelogue_types.sea import SeaCompany, SeaLine, SeaStop, SeaDock, SeaConnection
from gatelogue_types.rail import RailCompany, RailLine, RailStation, RailPlatform, RailConnection
from gatelogue_types.spawn_warp import SpawnWarp
from gatelogue_types.town import Town

if TYPE_CHECKING:
    # pyrefly: ignore [missing-import]
    from collections.abc import Iterator

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

        return cls.from_bytes(httpx.get(URL, *args, **kwargs).content)

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
        if ty is None or ty is Node:
            return Node.auto_type(self.conn, i)
        elif ty is LocatedNode:
            return LocatedNode.auto_type(self.conn, i)
        return ty(self.conn, i)

    def nodes[T: Node = Node](self, ty: type[T] | None = None) -> Iterator[T]:
        if ty is None or ty is Node:
            return (
                Node.STR2TYPE[ty](self.conn, i) for i, ty in self.conn.execute("SELECT i FROM Node").fetchall()
            )
        if ty is LocatedNode:
            return (
                Node.STR2TYPE[ty](self.conn, i) for i, ty in self.conn.execute("SELECT NodeLocation.i, type FROM NodeLocation LEFT JOIN Node on Node.i = NodeLocation.i").fetchall()
            )
        return (
            ty(self.conn, i)
            for (i,) in self.conn.execute("SELECT i FROM Node WHERE type = :type", dict(type=ty.__name__))
        )

    def __iter__(self) -> Iterator[Node]:
        return self.nodes()

    def __len__(self):
        return self.conn.execute("SELECT count(rowid) FROM Node").fetchone()[0]
