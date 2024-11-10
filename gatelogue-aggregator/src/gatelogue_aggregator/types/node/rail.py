from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, Self, override

from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.connections import Connection
from gatelogue_aggregator.types.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef, World
from gatelogue_aggregator.types.source import Source, Sourced

if TYPE_CHECKING:
    from collections.abc import Iterable


class RailSource(BaseContext, Source):
    pass


class RailCompany(Node[RailSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (RailLine, RailStation)

    name: str
    """Name of the Rail company"""

    lines: list[Sourced[int]] = None
    """List of IDs of all :py:class:`RailLine` s the company operates"""
    stations: list[Sourced[int]] = None
    """List of all :py:class:`RailStation` s the company's lines stop at"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: RailSource,
        *,
        name: str,
        lines: Iterable[RailLine] | None = None,
        stations: Iterable[RailStation] | None = None,
    ):
        self = super().new(ctx, name=name)
        if lines is not None:
            for line in lines:
                self.connect(ctx, line)
        if stations is not None:
            for station in stations:
                self.connect(ctx, station)
        return self

    @override
    def str_ctx(self, ctx: RailSource) -> str:
        return self.name

    @override
    def equivalent(self, ctx: RailSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, ctx: RailSource, other: Self):
        pass

    @override
    def merge_key(self, ctx: RailSource) -> str:
        return self.name

    @override
    def prepare_export(self, ctx: RailSource):
        self.lines = self.get_all_id(ctx, RailLine)
        self.stations = self.get_all_id(ctx, RailStation)

    @override
    def ref(self, ctx: RailSource) -> NodeRef[Self]:
        return NodeRef(RailCompany, name=self.name)


class RailLine(Node[RailSource], kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (RailCompany, RailStation)

    code: str
    """Unique code identifying the Rail line"""
    name: Sourced[str] | None = None
    """Name of the line"""
    colour: Sourced[str] | None = None
    """Colour of the line (on a map)"""
    mode: Sourced[Literal["warp", "cart", "traincart", "vehicles"]] | None = None
    """Type of rail or rail technology used on the line"""

    company: Sourced[int] = None
    """ID of the :py:class:`RailCompany` that operates the line"""
    ref_station: Sourced[int] | None = None
    """ID of one :py:class:`RailStation` on the line, typically a terminus"""

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: RailSource,
        *,
        code: str,
        company: RailCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: Literal["warp", "cart", "traincart", "vehicles"] | None = None,
        ref_station: RailStation | None = None,
    ):
        self = super().new(ctx, code=code)
        self.connect_one(ctx, company)
        if name is not None:
            self.name = ctx.source(name)
        if colour is not None:
            self.colour = ctx.source(colour)
        if mode is not None:
            self.mode = ctx.source(mode)
        if ref_station is not None:
            self.connect_one(ctx, ref_station)
        return self

    @override
    def str_ctx(self, ctx: RailSource) -> str:
        code = self.code
        company = self.get_one(ctx, RailCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: RailSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(ctx, RailCompany).equivalent(
            ctx, other.get_one(ctx, RailCompany)
        )

    @override
    def merge_attrs(self, ctx: RailSource, other: Self):
        self._merge_sourced(ctx, other, "name")
        self._merge_sourced(ctx, other, "colour")
        self._merge_sourced(ctx, other, "mode")

    @override
    def merge_key(self, ctx: RailSource) -> str:
        return self.code

    @override
    def prepare_export(self, ctx: RailSource):
        self.company = self.get_one_id(ctx, RailCompany)
        self.ref_station = self.get_one_id(ctx, RailStation)

    @override
    def ref(self, ctx: RailSource) -> NodeRef[Self]:
        return NodeRef(RailLine, code=self.code, company=self.get_one(ctx, RailCompany).name)


class RailStation(LocatedNode[RailSource], kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (RailStation, RailLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (RailCompany,)

    codes: set[str]
    """Unique code(s) identifying the Rail station. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the station"""

    company: Sourced[int] = None
    """ID of the :py:class:`RailCompany` that stops here"""
    connections: dict[int, list[Sourced[RailConnection]]] = None
    """
    References all next stations on the lines serving this station.
    It is represented as a mapping of station IDs to a list of connection data (:py:class:`RailConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the station with ID ``1234`` is the next station from here on two lines.
    """

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        ctx: RailSource,
        *,
        codes: set[str],
        company: RailCompany,
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
    def str_ctx(self, ctx: RailSource) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(ctx, RailCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, ctx: RailSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(ctx, RailCompany).equivalent(
            ctx, other.get_one(ctx, RailCompany)
        )

    @override
    def merge_attrs(self, ctx: RailSource, other: Self):
        super().merge_attrs(ctx, other)
        self.codes.update(other.codes)
        self._merge_sourced(ctx, other, "name")

    @override
    def merge_key(self, ctx: RailSource) -> str:
        return self.get_one(ctx, RailCompany).name

    @override
    def prepare_export(self, ctx: RailSource):
        super().prepare_export(ctx)
        self.company = self.get_one_id(ctx, RailCompany)
        self.connections = {
            node.i: list(self.get_edges(ctx, node, RailConnection))
            for node in self.get_all(ctx, RailStation, RailConnection)
        }

    @override
    def ref(self, ctx: RailSource) -> NodeRef[Self]:
        return NodeRef(RailStation, codes=self.codes, company=self.get_one(ctx, RailCompany).name)


class RailConnection(Connection[RailSource, RailLine]):
    pass


class RailLineBuilder(LineBuilder[RailSource, RailLine, RailStation]):
    CnT = RailConnection
