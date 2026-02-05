from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, ClassVar, Literal, Self, TypedDict, Unpack

from gatelogue_types.base import _Column, _CoordinatesColumn, _FKColumn, _format_str, _SetAttr

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Callable, Iterable, Iterator


class Node:
    STR2TYPE: ClassVar[dict] = {}

    def __init_subclass__(cls, **kwargs):
        cls.STR2TYPE[cls.__name__] = cls

    def __init__(self, conn: sqlite3.Connection, i: int):
        self.conn = conn
        assert isinstance(i, int)
        self.i = i
        """The ID of the node"""

    @classmethod
    def auto_type(cls, conn: sqlite3.Connection, i: int):
        (ty,) = conn.execute("SELECT type FROM Node WHERE i = :i", dict(i=i)).fetchone()
        return cls.STR2TYPE[ty](conn, i)

    type = _Column[str]("type", "Node")
    """The type of the node"""
    sources = _SetAttr[int]("NodeSource", "source")
    """All sources that prove the node's existence"""
    COLUMNS: ClassVar[tuple[_Column | _FKColumn | _SetAttr | _CoordinatesColumn, ...]] = ()

    @property
    def source(self) -> int:
        sources = self.sources
        assert len(sources) == 1, "Expected only one source"
        return next(iter(sources))

    @source.setter
    def source(self, value: int):
        self.sources = {value}

    def __str__(self):
        return type(self).__name__ + f"({self.i})"

    @classmethod
    def create_node(cls, conn: sqlite3.Connection, src: int, *, ty: str) -> int:
        cur = conn.cursor()
        cur.execute("INSERT INTO Node ( type ) VALUES ( :type )", dict(type=ty))
        (i,) = cur.execute("SELECT i FROM Node WHERE ROWID = last_insert_rowid()").fetchone()
        cur.execute("INSERT INTO NodeSource ( i, source ) VALUES ( :i, :source )", dict(i=i, source=src))
        return i

    def __eq__(self, other: Self) -> bool:
        return self.i == other.i

    def __hash__(self):
        return hash(self.i)

    def equivalent_nodes(self) -> Iterator[Self]:
        raise NotImplementedError

    def _merge(self, other: Self):
        raise NotImplementedError

    def merge(self, other: Self, warn_fn: Callable[[str], object] = warnings.warn):
        if self == other:
            warn_fn(f"{self} tried to merge with itself")
            return
        self_str = str(self)
        other_str = str(other)
        for attr in self.COLUMNS:
            attr._merge(self, other, self_str, other_str, warn_fn)

        self._merge(other)

        cur = self.conn.cursor()
        cur.execute("DELETE FROM NodeSource WHERE i = :i", dict(i=other.i))
        cur.execute("DELETE FROM Node WHERE i = :i", dict(i=other.i))

    @classmethod
    def format_create_kwargs(cls, **kwargs) -> dict:
        for attr in cls.COLUMNS:
            key = (attr.table_column + "s" if isinstance(attr, _SetAttr) else attr.name).strip('"')
            if key == "from":
                key += "_"
            if key not in kwargs:
                kwargs[key] = None
            if isinstance(attr, _Column):
                if attr.formatter is not None:
                    kwargs[key] = attr.formatter(kwargs[key])
                if attr.sourced:
                    kwargs[key + "_src"] = kwargs[key] is not None
            elif isinstance(attr, _SetAttr):
                if attr.formatter is not None:
                    kwargs[key] = {attr.formatter(value) for value in kwargs[key]} if kwargs[key] is not None else set()
                if attr.sourced:
                    kwargs[key + "_src"] = kwargs[key] is not None and len(kwargs[key]) > 0
            elif isinstance(attr, _FKColumn):
                kwargs[key] = kwargs[key].i if kwargs[key] is not None else None
                if attr.sourced:
                    kwargs[key + "_src"] = kwargs[key] is not None
            elif isinstance(attr, _CoordinatesColumn):
                kwargs["coordinates_src"] = kwargs["coordinates"] is not None
                kwargs["x"] = int(kwargs["coordinates"][0]) if kwargs["coordinates"] is not None else None
                kwargs["y"] = int(kwargs["coordinates"][1]) if kwargs["coordinates"] is not None else None
        return kwargs


type World = Literal["New", "Old", "Space"]


class LocatedNode(Node):
    world = _Column[World | None]("world", "NodeLocation", sourced=True, formatter=_format_str)
    """The world the node is in"""
    coordinates = _CoordinatesColumn()
    """The coordinates of the node"""
    COLUMNS: ClassVar = (world, coordinates)

    @classmethod
    def auto_type(cls, conn: sqlite3.Connection, i: int) -> LocatedNode:
        (ty,) = conn.execute(
            "SELECT type FROM NodeLocation LEFT JOIN Node on Node.i = NodeLocation.i WHERE NodeLocation.i = :i",
            dict(i=i),
        ).fetchone()
        return cls.STR2TYPE[ty](conn, i)

    class CreateParams(TypedDict, total=False):
        world: World | None
        coordinates: tuple[int, int] | None

    @classmethod
    def create_node_with_location(
        cls, conn: sqlite3.Connection, src: int, *, ty: str, **kwargs: Unpack[CreateParams]
    ) -> int:
        i = cls.create_node(conn, src, ty=ty)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO NodeLocation (i, world, x, y) VALUES (:i, :world, :x, :y)",
            dict(i=i, **kwargs),
        )
        cur.execute(
            "INSERT INTO NodeLocationSource (i, source, world, coordinates) VALUES (:i, :source, :world_src, :coordinates_src)",
            dict(i=i, source=src, **kwargs),
        )
        return i

    @property
    def _nodes_in_proximity(self) -> Iterator[int]:
        return (
            j if self.i == i else i
            for i, j in self.conn.execute(
                "SELECT node1, node2 FROM Proximity WHERE node1 = :i OR node2 = :i", dict(i=self.i)
            ).fetchall()
        )

    @property
    def nodes_in_proximity(self) -> Iterator[tuple[LocatedNode, Proximity]]:
        """
        References all nodes that are near (within walking distance of) this object.

        :return: Pairs of nodes in proximity as well as proximity data (:py:class:`Proximity`).
        """
        return (
            (o_node := LocatedNode.auto_type(self.conn, o), Proximity(self.conn, self, o_node))
            for o in self._nodes_in_proximity
        )

    @property
    def _shared_facilities(self) -> Iterator[int]:
        return (
            j if self.i == i else i
            for i, j in self.conn.execute(
                "SELECT node1, node2 FROM SharedFacility WHERE node1 = :i OR node2 = :i", dict(i=self.i)
            ).fetchall()
        )

    @property
    def shared_facilities(self) -> Iterable[LocatedNode]:
        """References all nodes that this object shares the same facility with (same building, station, hub etc)"""
        return (LocatedNode.auto_type(self.conn, o) for o in self._shared_facilities)

    def _merge(self, other: Self):
        cur = self.conn.cursor()
        cur.execute("UPDATE OR FAIL SharedFacility SET node1 = :i1 WHERE node1 = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE OR FAIL SharedFacility SET node2 = :i1 WHERE node2 = :i2", dict(i1=self.i, i2=other.i))
        cur.execute(
            "INSERT INTO Proximity SELECT min(node2, :i1), max(node2, :i1), distance, explicit FROM Proximity "
            "WHERE node1 = :i2 ON CONFLICT (node1, node2) DO NOTHING",
            dict(i1=self.i, i2=other.i),
        )
        cur.execute(
            "INSERT INTO Proximity SELECT min(node1, :i1), max(node1, :i1), distance, explicit FROM Proximity "
            "WHERE node2 = :i2 ON CONFLICT (node1, node2) DO NOTHING",
            dict(i1=self.i, i2=other.i),
        )
        cur.execute("UPDATE OR FAIL ProximitySource SET (node1, node2) = (min(node2, :i1), max(node2, :i1)) WHERE node1 = :i2", dict(i1=self.i, i2=other.i))
        cur.execute("UPDATE OR FAIL ProximitySource SET (node1, node2) = (min(node1, :i1), max(node1, :i1)) WHERE node2 = :i2", dict(i1=self.i, i2=other.i))
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
        if node1.i > node2.i:
            node1, node2 = node2, node1

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Proximity (node1, node2, distance, explicit) VALUES (:node1, :node2, :distance, :explicit) ON CONFLICT DO NOTHING",
            dict(node1=node1.i, node2=node2.i, distance=distance, explicit=explicit),
        )
        cur.executemany(
            "INSERT INTO ProximitySource ( node1, node2, source ) VALUES ( :node1, :node2, :source ) ON CONFLICT DO NOTHING",
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
        if node1.i > node2.i:
            node1, node2 = node2, node1

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO SharedFacility (node1, node2) VALUES (:node1, :node2) ON CONFLICT DO NOTHING ", dict(node1=node1.i, node2=node2.i)
        )
        return cls(conn, node1, node2)
