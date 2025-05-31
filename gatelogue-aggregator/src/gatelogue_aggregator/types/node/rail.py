from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self, override

import gatelogue_types as gt
import rich

from gatelogue_aggregator.logging import ERROR, RESULT
from gatelogue_aggregator.types.edge.connections import Connection
from gatelogue_aggregator.types.edge.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef
from gatelogue_aggregator.types.source import Source

if TYPE_CHECKING:
    from collections.abc import Iterable


class RailSource(Source):
    @classmethod
    @override
    def reported_nodes(cls) -> tuple[type[Node], ...]:
        return (
            (RailCompany,)
            if cls.__name__.startswith("Dynmap") or cls.__name__.endswith("Warp")
            else (RailCompany, RailLine)
        )


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

    @override
    def report(self, src: RailSource):
        num_lines = len(list(self.get_all(src, RailLine)))
        num_stations = len(list(self.get_all(src, RailStation)))
        colour = ERROR if (num_lines == 0 and not src.is_warp_source()) or num_stations == 0 else RESULT
        self.print_report(src, colour,
            f"has {num_lines} lines and {num_stations} stations"
        )


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

    @override
    def report(self, src: RailSource):
        num_stations = len(
            [
                stn
                for stn in self.get_one(src, RailCompany).get_all(src, RailStation)
                if any(
                    conn.v.line.refs(src, self)
                    for node in stn.get_all(src, RailStation, RailConnection)
                    for conn in stn.get_edges(src, node, RailConnection)
                )
            ]
        )
        colour = ERROR if num_stations == 0 else RESULT
        self.print_report(src, colour, f"has {num_stations} stations")


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
        codes = "/".join(self.codes)
        code = codes if (name := self.name) is None or name.v in codes else f"{name.v} ({codes})"
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

    @override
    def report(self, src: RailSource):
        super().report(src)
        num_connections = len(list(self.get_all(src, RailStation, RailConnection)))
        if num_connections == 0:
            self.print_report(src, ERROR, "has no connections")


class RailConnection(Connection[RailLine]):
    pass


class RailLineBuilder(LineBuilder[RailLine, RailStation]):
    CnT = RailConnection
