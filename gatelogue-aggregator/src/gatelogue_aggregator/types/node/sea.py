from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal, Self, override, ClassVar

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef
from gatelogue_aggregator.types.source import Source, Sourced

if TYPE_CHECKING:
    from collections.abc import Iterable


class _SeaContext(BaseContext, Source):
    pass


class SeaCompany(Node[_SeaContext], kw_only=True):
    acceptable_list_node_types: ClassVar = lambda: (SeaLine, SeaStop)  # noqa: E731

    name: str
    """Name of the Sea company"""

    lines: list[Sourced[int]] = None
    """List of IDs of all :py:class:`SeaLine` s the company operates"""
    stops: list[Sourced[int]] = None
    """List of all :py:class:`SeaStop` s the company's lines stop at"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SeaContext,
        *,
        name: str,
        lines: Iterable[SeaLine] | None = None,
        stops: Iterable[SeaStop] | None = None,
    ):
        self = super().new(ctx, name=name)
        if lines is not None:
            for line in lines:
                self.connect(ctx, line, ctx.source(None))
        if stops is not None:
            for stop in stops:
                self.connect(ctx, stop, ctx.source(None))
        return self

    @override
    def str_ctx(self, ctx: SeaContext) -> str:
        return self.name

    @override
    def equivalent(self, ctx: SeaContext, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: SeaContext, other: Self):
        pass

    @override
    def merge_key(self, ctx: SeaContext) -> str:
        return self.name

    @override
    def prepare_export(self, ctx: SeaContext):
        self.lines = self.get_all_id(ctx, SeaLine)
        self.stops = self.get_all_id(ctx, SeaStop)

    @override
    def ref(self, ctx: SeaContext) -> NodeRef[Self]:
        return NodeRef(SeaCompany, name=self.name)


class SeaLine(Node[_SeaContext], kw_only=True):
    acceptable_single_node_types: ClassVar = lambda: (SeaCompany, SeaStop)  # noqa: E731

    code: str
    """Unique code identifying the Sea line"""
    name: Sourced[str] | None = None
    """Name of the line"""
    colour: Sourced[str] | None = None
    """Colour of the line (on a map)"""

    company: Sourced[int] = None
    """ID of the :py:class:`SeaCompany` that operates the line"""
    ref_stop: Sourced[int] | None = None
    """ID of one :py:class:`SeaStop` on the line, typically a terminus"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SeaContext,
        *,
        code: str,
        company: SeaCompany,
        name: str | None = None,
        colour: str | None = None,
        ref_stop: SeaStop | None = None,
    ):
        self = super().new(ctx, code=code)
        self.connect_one(ctx, company, ctx.source(None))
        if name is not None:
            self.name = ctx.source(name)
        if colour is not None:
            self.colour = ctx.source(colour)
        if ref_stop is not None:
            self.connect_one(ctx, ref_stop, ctx.source(None))
        return self

    @override
    def str_ctx(self, ctx: SeaContext) -> str:
        code = self.code
        company = self.get_one(ctx, SeaCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: SeaContext, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, SeaCompany).equivalent(ctx, other.get_one(ctx, SeaCompany))

    @override
    def merge_attrs(self, ctx: SeaContext, other: Self):
        self.name.merge(ctx, other.name)
        self.colour.merge(ctx, other.colour)

    @override
    def merge_key(self, ctx: SeaContext) -> str:
        return self.code

    @override
    def prepare_export(self, ctx: SeaContext):
        self.company = self.get_one_id(ctx, SeaCompany)
        self.ref_stop = self.get_one_id(ctx, SeaStop)

    @override
    def ref(self, ctx: SeaContext) -> NodeRef[Self]:
        return NodeRef(SeaLine, code=self.code, company=self.get_one(ctx, SeaCompany).name)


class SeaStop(LocatedNode[_SeaContext], kw_only=True):
    acceptable_list_node_types: ClassVar = lambda: (SeaStop, SeaLine, LocatedNode)  # noqa: E731
    acceptable_single_node_types: ClassVar = lambda: (SeaCompany,)  # noqa: E731

    codes: set[str]
    """Unique code(s) identifying the Sea stop. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the stop"""

    company: Sourced[int] = None
    """ID of the :py:class:`SeaCompany` that stops here"""
    connections: dict[int, list[Sourced[SeaConnection]]] = None
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`SeaConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SeaContext,
        *,
        codes: set[str],
        company: SeaCompany,
        name: str | None = None,
        world: Literal["New", "Old"] | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        self = super().new(ctx, world=world, coordinates=coordinates, codes=codes)
        self.connect_one(ctx, company, ctx.source(None))
        if name is not None:
            self.name = ctx.source(name)
        return self

    @override
    def str_ctx(self, ctx: SeaContext) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, SeaCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: SeaContext, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, SeaCompany).equivalent(
            ctx, other.get_one(ctx, SeaCompany)
        )

    @override
    def merge_attrs(self, ctx: SeaContext, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: SeaContext) -> str:
        return self.get_one(ctx, SeaCompany).name

    @override
    def prepare_export(self, ctx: SeaContext):
        super().prepare_export(ctx)
        self.company = self.get_one_id(ctx, SeaCompany)
        self.connections = {
            node.i: list(self.get_edges(ctx, node, Sourced[SeaConnection])) for node in self.get_all(ctx, SeaStop)
        }

    @override
    def ref(self, ctx: SeaContext) -> NodeRef[Self]:
        return NodeRef(SeaStop, codes=self.codes, company=self.get_one(ctx, SeaCompany).name)


class SeaConnection(Connection[_SeaContext, SeaLine]):
    pass


class SeaLineBuilder(LineBuilder[_SeaContext, SeaLine, SeaStop]):
    CnT = SeaConnection


class SeaContext(_SeaContext):
    pass


type SeaSource = SeaContext
