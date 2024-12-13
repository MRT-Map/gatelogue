from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self, override

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef, World
from gatelogue_aggregator.types.source import Source, Sourced

if TYPE_CHECKING:
    from collections.abc import Iterable


class BusSource(BaseContext, Source):
    pass


class BusCompany(Node[BusSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (BusLine, BusStop)

    name: str
    """Name of the bus company"""

    lines: list[Sourced[int]] = None
    """List of IDs of all :py:class:`BusLine` s the company operates"""
    stops: list[Sourced[int]] = None
    """List of all :py:class:`BusStop` s the company's lines stop at"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: BusSource,
        *,
        name: str,
        lines: Iterable[BusLine] | None = None,
        stops: Iterable[BusStop] | None = None,
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
    def str_ctx(self, ctx: BusSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: BusSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: BusSource, other: Self):
        pass

    @override
    def merge_key(self, ctx: BusSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        self.name = str(self.name).strip()

    @override
    def prepare_export(self, ctx: BusSource):
        self.lines = self.get_all_id(ctx, BusLine)
        self.stops = self.get_all_id(ctx, BusStop)

    @override
    def ref(self, ctx: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusCompany, name=self.name)


class BusLine(Node[BusSource], kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (BusCompany, BusStop)

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

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: BusSource,
        *,
        code: str,
        company: BusCompany,
        name: str | None = None,
        colour: str | None = None,
        ref_stop: BusStop | None = None,
    ):
        self = super().new(ctx, code=code)
        self.connect_one(ctx, company)
        if name is not None:
            self.name = ctx.source(name)
        if colour is not None:
            self.colour = ctx.source(colour)
        if ref_stop is not None:
            self.connect_one(ctx, ref_stop)
        return self

    @override
    def str_ctx(self, ctx: BusSource) -> str:
        code = self.code
        company = self.get_one(ctx, BusCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: BusSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, BusCompany).equivalent(ctx, other.get_one(ctx, BusCompany))

    @override
    def merge_attrs(self, ctx: BusSource, other: Self):
        self._merge_sourced(ctx, other, "name")
        self._merge_sourced(ctx, other, "colour")

    @override
    def merge_key(self, ctx: BusSource) -> str:
        return self.code

    @override
    def sanitise_strings(self):
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.colour is not None:
            self.colour.v = str(self.colour.v).strip()

    @override
    def prepare_export(self, ctx: BusSource):
        self.company = self.get_one_id(ctx, BusCompany)
        self.ref_stop = self.get_one_id(ctx, BusStop)

    @override
    def ref(self, ctx: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusLine, code=self.code, company=self.get_one(ctx, BusCompany).name)


class BusStop(LocatedNode[BusSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (BusStop, BusLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (BusCompany,)

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

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: BusSource,
        *,
        codes: set[str],
        company: BusCompany,
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
    def str_ctx(self, ctx: BusSource) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, BusCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: BusSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, BusCompany).equivalent(
            ctx, other.get_one(ctx, BusCompany)
        )

    @override
    def merge_attrs(self, ctx: BusSource, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: BusSource) -> str:
        return self.get_one(ctx, BusCompany).name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.codes = {str(a).strip() for a in self.codes}
        if self.name is not None:
            self.name.v = str(self.name.v).strip()

    @override
    def prepare_export(self, ctx: BusSource):
        super().prepare_export(ctx)
        self.company = self.get_one_id(ctx, BusCompany)
        self.connections = {
            node.i: list(self.get_edges(ctx, node, BusConnection)) for node in self.get_all(ctx, BusStop)
        }

    @override
    def ref(self, ctx: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusStop, codes=self.codes, company=self.get_one(ctx, BusCompany).name)


class BusConnection(Connection[BusSource, BusLine]):
    pass


class BusLineBuilder(LineBuilder[BusSource, BusLine, BusStop]):
    CnT = BusConnection
