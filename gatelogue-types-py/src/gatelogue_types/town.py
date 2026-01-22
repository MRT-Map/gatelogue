from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self, Unpack

from gatelogue_types.base import _Column, _format_str
from gatelogue_types.node import LocatedNode

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterator

type Rank = Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]


class Town(LocatedNode):
    name = _Column[str]("name", "Town", formatter=_format_str)
    """Name of the town"""
    rank = _Column[Rank]("rank", "Town", formatter=_format_str)
    """Rank of the town"""
    mayor = _Column[str]("mayor", "Town", formatter=_format_str)
    """Mayor of the town"""
    deputy_mayor = _Column[str | None]("deputyMayor", "Town", formatter=_format_str)
    """Deputy Mayor of the town"""
    COLUMNS: ClassVar = (*LocatedNode.COLUMNS, name, rank, mayor, deputy_mayor)

    class CreateParams(LocatedNode.CreateParams, total=True):
        name: str
        rank: Rank
        mayor: str
        deputy_mayor: str | None

    @classmethod
    def create(cls, conn: sqlite3.Connection, src: int, **kwargs: Unpack[CreateParams]) -> Self:
        kwargs = cls.format_create_kwargs(**kwargs)
        i = cls.create_node_with_location(conn, src, ty=cls.__name__, **kwargs)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Town (i, name, rank, mayor, deputyMayor) VALUES (:i, :name, :rank, :mayor, :deputy_mayor)",
            dict(i=i, **kwargs),
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
