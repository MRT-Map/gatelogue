from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from typing import Literal, Self, Unpack

from gatelogue_types.base import _Column
from gatelogue_types.node import LocatedNode

type WarpType = Literal["premier", "terminus", "traincarts", "portal", "misc"]


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
