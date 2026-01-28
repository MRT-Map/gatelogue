from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self, Unpack

from gatelogue_types.base import _Column, _format_str
from gatelogue_types.node import LocatedNode

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterator

type WarpType = Literal["premier", "terminus", "traincarts", "portal", "misc"]


class SpawnWarp(LocatedNode):
    name = _Column[str]("name", "SpawnWarp", formatter=_format_str)
    """Name of the spawn warp"""
    warp_type = _Column[WarpType]("warpType", "SpawnWarp", formatter=_format_str)
    """The type of the spawn warp"""
    COLUMNS: ClassVar = (*LocatedNode.COLUMNS, name, warp_type)

    def __str__(self):
        return super().__str__() + f" {self.name} ({self.warp_type})"

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
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO SpawnWarp (i, name, warpType) VALUES (:i, :name, :warp_type)",
            dict(i=i, **kwargs),
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
