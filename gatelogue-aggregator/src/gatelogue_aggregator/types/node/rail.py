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


class _RailContext(BaseContext, Source):
    pass


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailCompany(Node[_RailContext]):
    acceptable_list_node_types = lambda: (RailLine, RailStation)  # noqa: E731

    name: str
    """Name of the Rail company"""

    lines: list[Sourced[int]] = None
    """List of IDs of all :py:class:`RailLine` s the company operates"""
    stops: list[Sourced[int]] = None
    """List of all :py:class:`RailStation` s the company's lines stop at"""

    @override
    def __init__(
        self,
        ctx: RailContext,
        *,
        name: str,
        lines: Iterable[RailLine] | None = None,
        stops: Iterable[RailStation] | None = None,
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
    def str_ctx(self, ctx: RailContext) -> str:
        return self.name

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: RailContext, other: Self):
        pass

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.name

    @override
    def prepare_export(self, ctx: RailContext):
        self.lines = self.get_all_id(ctx, RailLine)
        self.stops = self.get_all_id(ctx, RailStation)

    @override
    def ref(self, ctx: RailContext) -> NodeRef[Self]:
        return NodeRef(RailCompany, name=self.name)


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailLine(Node[_RailContext]):
    acceptable_single_node_types = lambda: (RailCompany, RailStation)  # noqa: E731

    code: str
    """Unique code identifying the Rail line"""
    name: Sourced[str] | None = None
    """Name of the line"""
    colour: Sourced[str] | None = None
    """Colour of the line (on a map)"""

    company: Sourced[int] = None
    """ID of the :py:class:`RailCompany` that operates the line"""
    ref_stop: Sourced[int] | None = None
    """ID of one :py:class:`RailStation` on the line, typically a terminus"""

    @override
    def __init__(
        self,
        ctx: RailContext,
        *,
        code: str,
        company: RailCompany,
        name: str | None = None,
        colour: str | None = None,
        ref_stop: RailStation | None = None,
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
    def str_ctx(self, ctx: RailContext) -> str:
        code = self.code
        company = self.get_one(ctx, RailCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, RailCompany).equivalent(
            ctx, other.get_one(ctx, RailCompany)
        )

    @override
    def merge_attrs(self, ctx: RailContext, other: Self):
        self.name.merge(ctx, other.name)
        self.colour.merge(ctx, other.colour)

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.code

    @override
    def prepare_export(self, ctx: RailContext):
        self.company = self.get_one_id(ctx, RailCompany)
        self.ref_stop = self.get_one_id(ctx, RailStation)

    @override
    def ref(self, ctx: RailContext) -> NodeRef[Self]:
        return NodeRef(RailLine, code=self.code, company=self.get_one(ctx, RailCompany).name)


@dataclasses.dataclass(unsafe_hash=True, kw_only=True)
class RailStation(LocatedNode[_RailContext]):
    acceptable_list_node_types = lambda: (RailStation, RailLine, LocatedNode)  # noqa: E731
    acceptable_single_node_types = lambda: (RailCompany,)  # noqa: E731

    codes: set[str]
    """Unique code(s) identifying the Rail stop. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the stop"""

    company: Sourced[int] = None
    """ID of the :py:class:`RailCompany` that stops here"""
    connections: dict[int, list[Sourced[RailConnection]]] = None
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`RailConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """

    @override
    def __init__(
        self,
        ctx: RailContext,
        *,
        codes: set[str],
        company: RailCompany,
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
    def str_ctx(self, ctx: RailContext) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, RailCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: RailContext, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, RailCompany).equivalent(
            ctx, other.get_one(ctx, RailCompany)
        )

    @override
    def merge_attrs(self, ctx: RailContext, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: RailContext) -> str:
        return self.get_one(ctx, RailCompany).name

    @override
    def prepare_export(self, ctx: RailContext):
        super().prepare_export(ctx)
        self.company = self.get_one_id(ctx, RailCompany)
        self.connections = {
            node.i: [a for a in self.get_edges(ctx, node, Sourced[RailConnection])]
            for node in self.get_all(ctx, RailStation)
        }

    @override
    def ref(self, ctx: RailContext) -> NodeRef[Self]:
        return NodeRef(RailStation, codes=self.codes, company=self.get_one(ctx, RailCompany).name)


class RailConnection(Connection[_RailContext, RailLine]):
    pass


class RailLineBuilder(LineBuilder[_RailContext, RailLine, RailStation]):
    CnT = RailConnection


class RailContext(_RailContext):
    pass


type RailSource = RailContext
