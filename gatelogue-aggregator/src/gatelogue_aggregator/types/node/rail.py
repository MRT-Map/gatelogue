from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self, override

import gatelogue_types as gt

from gatelogue_aggregator.types.edge.connections import Connection
from gatelogue_aggregator.types.edge.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef
from gatelogue_aggregator.types.source import Source

if TYPE_CHECKING:
    from collections.abc import Iterable


class RailSource(Source):
    pass


class RailCompany(gt.RailCompany, Node, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (RailLine, RailStation)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: RailSource,
        *,
        name: str,
        lines: Iterable[RailLine] | None = None,
        stations: Iterable[RailStation] | None = None,
        local: bool = False,
    ):
        self = super().new(src, name=name, local=local)
        if lines is not None:
            for line in lines:
                self.connect(src, line)
        if stations is not None:
            for station in stations:
                self.connect(src, station)
        return self

    @override
    def str_src(self, src: RailSource) -> str:
        return self.name

    @override
    def equivalent(self, src: RailSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, src: RailSource, other: Self):
        self.local = self.local or other.local

    @override
    def merge_key(self, src: RailSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        self.name = str(self.name).strip()

    @override
    def export(self, src: RailSource) -> gt.RailCompany:
        return gt.RailCompany(
            **self._as_dict(src),
        )

    @override
    def _as_dict(self, src: RailSource) -> dict:
        return super()._as_dict(src) | {
            "lines": self.get_all_id(src, RailLine),
            "stations": self.get_all_id(src, RailStation),
        }

    @override
    def ref(self, src: RailSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(RailCompany, name=self.name)


class RailLine(gt.RailLine, Node, kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (RailCompany, RailStation)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: RailSource,
        *,
        code: str,
        company: RailCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: gt.RailMode | None = None,
        ref_station: RailStation | None = None,
    ):
        self = super().new(src, code=code)
        self.connect_one(src, company)
        if name is not None:
            self.name = src.source(name)
        if colour is not None:
            self.colour = src.source(colour)
        if mode is not None:
            self.mode = src.source(mode)
        if ref_station is not None:
            self.connect_one(src, ref_station)
        return self

    @override
    def str_src(self, src: RailSource) -> str:
        code = self.code
        company = self.get_one(src, RailCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, src: RailSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(src, RailCompany).equivalent(
            src, other.get_one(src, RailCompany)
        )

    @override
    def merge_attrs(self, src: RailSource, other: Self):
        self._merge_sourced(src, other, "name")
        self._merge_sourced(src, other, "colour")
        self._merge_sourced(src, other, "mode")

    @override
    def merge_key(self, src: RailSource) -> str:
        return self.code

    @override
    def sanitise_strings(self):
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.colour is not None:
            self.colour.v = str(self.colour.v).strip()
        if self.mode is not None:
            self.mode.v = str(self.mode.v).strip()

    @override
    def export(self, src: RailSource) -> gt.RailLine:
        return gt.RailLine(
            **self._as_dict(src),
        )

    @override
    def _as_dict(self, src: RailSource) -> dict:
        return super()._as_dict(src) | {
            "company": self.get_one_id(src, RailCompany),
            "ref_station": self.get_one_id(src, RailStation),
        }

    @override
    def ref(self, src: RailSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(RailLine, code=self.code, company=self.get_one(src, RailCompany).name)


class RailStation(gt.RailStation, LocatedNode, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (RailStation, RailLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (RailCompany,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: RailSource,
        *,
        codes: set[str],
        company: RailCompany,
        name: str | None = None,
        world: gt.World | None = None,
        coordinates: tuple[float, float] | None = None,
    ):
        self = super().new(src, world=world, coordinates=coordinates, codes=codes)
        self.connect_one(src, company)
        if name is not None:
            self.name = src.source(name)
        return self

    @override
    def str_src(self, src: RailSource) -> str:
        code = "/".join(self.codes) if (code := self.name) is None else code.v
        company = self.get_one(src, RailCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, src: RailSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(src, RailCompany).equivalent(
            src, other.get_one(src, RailCompany)
        )

    @override
    def merge_attrs(self, src: RailSource, other: Self):
        super().merge_attrs(src, other)
        self.codes.update(other.codes)
        self._merge_sourced(src, other, "name")

    @override
    def merge_key(self, src: RailSource) -> str:
        return self.get_one(src, RailCompany).name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.codes = {str(a).strip() for a in self.codes}
        if self.name is not None:
            self.name.v = str(self.name.v).strip()

    @override
    def export(self, src: RailSource) -> gt.RailStation:
        return gt.RailStation(
            **self._as_dict(src),
        )

    @override
    def _as_dict(self, src: RailSource) -> dict:
        return super()._as_dict(src) | {
            "company": self.get_one_id(src, RailCompany),
            "connections": {
                node.i: [a.export(src) for a in self.get_edges(src, node, RailConnection)]
                for node in self.get_all(src, RailStation, RailConnection)
            },
        }

    @override
    def ref(self, src: RailSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(RailStation, codes=self.codes, company=self.get_one(src, RailCompany).name)


class RailConnection(Connection[RailLine]):
    pass


class RailLineBuilder(LineBuilder[RailLine, RailStation]):
    CnT = RailConnection
