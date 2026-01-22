from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from typing import Self, Unpack

from gatelogue_types.base import _Column
from gatelogue_types.node import LocatedNode


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
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
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
