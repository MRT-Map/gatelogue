from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Self, override, Literal

import msgspec

from gatelogue_aggregator.types.base import BaseContext, Source, Sourced
from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef

if TYPE_CHECKING:
    import uuid
    from collections.abc import Container, Iterable


class _BusContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class BusCompany(Node[_BusContext]):
    acceptable_list_node_types = lambda: (BusLine, BusStop)  # noqa: E731

    name: str
    """Name of the bus company"""

    lines: list[Sourced[int]] = None
    """List of IDs of all :py:class:`BusLine` s the company operates"""
    stops: list[Sourced[int]] = None
    """List of all :py:class:`BusStop` s the company's lines stop at"""

    @override
    def __init__(
        self,
        ctx: BusContext,
        *,
        name: str,
        lines: Iterable[BusLine] | None = None,
        stops: Iterable[BusStop] | None = None,
    ):
        super().__init__(ctx)
        self.name = name
        if lines is not None:
            for line in lines:
                self.connect(ctx, line, ctx.source(None))
        if stops is not None:
            for stop in stops:
                self.connect(ctx, stop, ctx.source(None))

    @override
    def str_ctx(self, ctx: BusContext) -> str:
        return self.name

    @override
    def equivalent(self, ctx: BusContext, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: BusContext, other: Self):
        pass

    @override
    def merge_key(self, ctx: BusContext) -> str:
        return self.name

    @override
    def prepare_export(self, ctx: BusContext):
        self.lines = self.get_all_id(ctx, BusLine)
        self.stops = self.get_all_id(ctx, BusStop)

    @override
    def ref(self, ctx: BusContext) -> NodeRef[Self]:
        return NodeRef(BusCompany, name=self.name)


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class BusLine(Node[_BusContext]):
    acceptable_single_node_types = lambda: (BusCompany, BusStop)  # noqa: E731

    code: str
    """Unique code identifying the bus line"""
    name: Sourced[str] | None = None
    """Name of the line"""
    colour: Sourced[str] | None = None
    """Colour of the line (on a map)"""

    company: Sourced[int] = None
    """ID of the :py:class:`BusCompany` that operates the line"""
    ref_stop: Sourced[int] | None = None
    """ID of one :py:class:`BusStop` on the line, typically a terminus"""

    @override
    def __init__(
        self,
        ctx: BusContext,
        *,
        code: str,
        company: BusCompany,
        name: str | None = None,
        colour: str | None = None,
        ref_stop: BusStop | None = None,
    ):
        super().__init__(ctx)
        self.code = code
        self.connect_one(ctx, company, ctx.source(None))
        if name is not None:
            self.name = ctx.source(name)
        if colour is not None:
            self.colour = ctx.source(colour)
        if ref_stop is not None:
            self.connect_one(ctx, ref_stop, ctx.source(None))

    @override
    def str_ctx(self, ctx: BusContext) -> str:
        code = self.code
        company = self.get_one(ctx, BusCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: BusContext, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, BusCompany).equivalent(ctx, other.get_one(ctx, BusCompany))

    @override
    def merge_attrs(self, ctx: BusContext, other: Self):
        self.name.merge(ctx, other.name)
        self.colour.merge(ctx, other.colour)

    @override
    def merge_key(self, ctx: BusContext) -> str:
        return self.code

    @override
    def prepare_export(self, ctx: BusContext):
        self.company = self.get_one_id(ctx, BusCompany)
        self.ref_stop = self.get_one_id(ctx, BusStop)

    @override
    def ref(self, ctx: BusContext) -> NodeRef[Self]:
        return NodeRef(BusLine, code=self.code, company=self.get_one(ctx, BusCompany).name)


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class BusStop(LocatedNode[_BusContext]):
    acceptable_list_node_types = lambda: (BusStop, BusLine, LocatedNode)  # noqa: E731
    acceptable_single_node_types = lambda: (BusCompany,)  # noqa: E731

    codes: set[str]
    """Unique code(s) identifying the bus stop. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the stop"""

    company: Sourced[int] = None
    """ID of the :py:class:`BusCompany` that stops here"""
    connections: dict[int, list[Sourced[BusConnection]]] = None
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`BusConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """

    @override
    def __init__(
        self,
        ctx: BusContext,
        *,
        codes: set[str],
        company: BusCompany,
        name: str | None = None,
        world: Literal["New", "Old"] | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        super().__init__(ctx, world=world, coordinates=coordinates)
        self.codes = codes
        self.connect_one(ctx, company, ctx.source(None))
        if name is not None:
            self.name = ctx.source(name)

    @override
    def str_ctx(self, ctx: BusContext) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, BusCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: BusContext, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, BusCompany).equivalent(
            ctx, other.get_one(ctx, BusCompany)
        )

    @override
    def merge_attrs(self, ctx: BusContext, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: BusContext) -> str:
        return self.get_one(ctx, BusCompany).name

    @override
    def prepare_export(self, ctx: BusContext):
        super().prepare_export(ctx)
        self.company = self.get_one_id(ctx, BusCompany)
        self.connections = {
            node.i: [a for a in self.get_edges(ctx, node, Sourced[BusConnection])]
            for node in self.get_all(ctx, BusStop)
        }

    @override
    def ref(self, ctx: BusContext) -> NodeRef[Self]:
        return NodeRef(BusStop, codes=self.codes, company=self.get_one(ctx, BusCompany).name)


class BusConnection(Connection[_BusContext, BusLine]):
    pass


class BusLineBuilder(LineBuilder[_BusContext, BusLine, BusStop]):
    CnT = BusConnection


class BusContext(_BusContext):
    pass


type BusSource = BusContext
