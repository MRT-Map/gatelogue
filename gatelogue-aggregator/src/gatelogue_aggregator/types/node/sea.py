from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self, override

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef, World
from gatelogue_aggregator.types.source import Source, Sourced

if TYPE_CHECKING:
    from collections.abc import Iterable


class SeaSource(BaseContext, Source):
    pass


class SeaCompany(Node[SeaSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (SeaLine, SeaStop)

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
        ctx: SeaSource,
        *,
        name: str,
        lines: Iterable[SeaLine] | None = None,
        stops: Iterable[SeaStop] | None = None,
    ):
        self = super().new(ctx, name=name)
        if lines is not None:
            for line in lines:
                self.connect(ctx, line)
        if stops is not None:
            for stop in stops:
                self.connect(ctx, stop)
        return self

    @override
    def str_ctx(self, ctx: SeaSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: SeaSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: SeaSource, other: Self):
        pass

    @override
    def merge_key(self, ctx: SeaSource) -> str:
        return self.name

    @override
    def prepare_merge(self):
        self.name = str(self.name).strip()

    @override
    def prepare_export(self, ctx: SeaSource):
        self.lines = self.get_all_id(ctx, SeaLine)
        self.stops = self.get_all_id(ctx, SeaStop)

    @override
    def ref(self, ctx: SeaSource) -> NodeRef[Self]:
        self.prepare_merge()
        return NodeRef(SeaCompany, name=self.name)


class SeaLine(Node[SeaSource], kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (SeaCompany, SeaStop)

    code: str
    """Unique code identifying the Sea line"""
    name: Sourced[str] | None = None
    """Name of the line"""
    colour: Sourced[str] | None = None
    """Colour of the line (on a map)"""
    mode: Sourced[Literal["ferry", "cruise"]] | None = None
    """Type of boat used on the line"""

    company: Sourced[int] = None
    """ID of the :py:class:`SeaCompany` that operates the line"""
    ref_stop: Sourced[int] | None = None
    """ID of one :py:class:`SeaStop` on the line, typically a terminus"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: SeaSource,
        *,
        code: str,
        company: SeaCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: Literal["ferry", "cruise"] | None = None,
        ref_stop: SeaStop | None = None,
    ):
        self = super().new(ctx, code=code)
        self.connect_one(ctx, company)
        if name is not None:
            self.name = ctx.source(name)
        if colour is not None:
            self.colour = ctx.source(colour)
        if mode is not None:
            self.mode = ctx.source(mode)
        if ref_stop is not None:
            self.connect_one(ctx, ref_stop)
        return self

    @override
    def str_ctx(self, ctx: SeaSource) -> str:
        code = self.code
        company = self.get_one(ctx, SeaCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: SeaSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, SeaCompany).equivalent(ctx, other.get_one(ctx, SeaCompany))

    @override
    def merge_attrs(self, ctx: SeaSource, other: Self):
        self._merge_sourced(ctx, other, "name")
        self._merge_sourced(ctx, other, "colour")
        self._merge_sourced(ctx, other, "mode")

    @override
    def merge_key(self, ctx: SeaSource) -> str:
        return self.code

    @override
    def prepare_merge(self):
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.colour is not None:
            self.colour.v = str(self.colour.v).strip()

    @override
    def prepare_export(self, ctx: SeaSource):
        self.company = self.get_one_id(ctx, SeaCompany)
        self.ref_stop = self.get_one_id(ctx, SeaStop)

    @override
    def ref(self, ctx: SeaSource) -> NodeRef[Self]:
        self.prepare_merge()
        return NodeRef(SeaLine, code=self.code, company=self.get_one(ctx, SeaCompany).name)


class SeaStop(LocatedNode[SeaSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (SeaStop, SeaLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (SeaCompany,)

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
        ctx: SeaSource,
        *,
        codes: set[str],
        company: SeaCompany,
        name: str | None = None,
        world: World | None = None,
        coordinates: tuple[int, int] | None = None,
    ):
        self = super().new(ctx, world=world, coordinates=coordinates, codes=codes)
        self.connect_one(ctx, company)
        if name is not None:
            self.name = ctx.source(name)
        return self

    @override
    def str_ctx(self, ctx: SeaSource) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, SeaCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: SeaSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, SeaCompany).equivalent(
            ctx, other.get_one(ctx, SeaCompany)
        )

    @override
    def merge_attrs(self, ctx: SeaSource, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: SeaSource) -> str:
        return self.get_one(ctx, SeaCompany).name

    @override
    def prepare_merge(self):
        super().prepare_merge()
        self.codes = {str(a).strip() for a in self.codes}
        if self.name is not None:
            self.name.v = str(self.name.v).strip()

    @override
    def prepare_export(self, ctx: SeaSource):
        super().prepare_export(ctx)
        self.company = self.get_one_id(ctx, SeaCompany)
        self.connections = {
            node.i: list(self.get_edges(ctx, node, SeaConnection)) for node in self.get_all(ctx, SeaStop)
        }

    @override
    def ref(self, ctx: SeaSource) -> NodeRef[Self]:
        self.prepare_merge()
        return NodeRef(SeaStop, codes=self.codes, company=self.get_one(ctx, SeaCompany).name)


class SeaConnection(Connection[SeaSource, SeaLine]):
    pass


class SeaLineBuilder(LineBuilder[SeaSource, SeaLine, SeaStop]):
    CnT = SeaConnection
