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


class BusSource(Source):
    @classmethod
    @override
    def reported_nodes(cls) -> tuple[type[Node], ...]:
        return (
            (BusCompany,)
            if cls.is_warp_source()
            else (BusCompany, BusLine)
        )


class BusCompany(gt.BusCompany, Node, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (BusLine, BusStop)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: BusSource,
        *,
        name: str,
        lines: Iterable[BusLine] | None = None,
        stops: Iterable[BusStop] | None = None,
        local: bool = False,
    ):
        self = super().new(src, name=name, local=local)
        if lines is not None:
            for line in lines:
                self.connect(src, line)
        if stops is not None:
            for stop in stops:
                self.connect(src, stop)
        return self

    @override
    def str_src(self, src: BusSource) -> str:
        return self.name

    @override
    def equivalent(self, src: BusSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, src: BusSource, other: Self):
        self.local = self.local or other.local

    @override
    def merge_key(self, src: BusSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        self.name = str(self.name).strip()

    @override
    def export(self, src: BusSource) -> gt.BusCompany:
        return gt.BusCompany(**self._as_dict(src))

    @override
    def _as_dict(self, src: BusSource) -> dict:
        return super()._as_dict(src) | {
            "lines": self.get_all_id(src, BusLine),
            "stops": self.get_all_id(src, BusStop),
        }

    @override
    def ref(self, src: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusCompany, name=self.name)

    @override
    def report(self, src: BusSource):
        num_lines = len(list(self.get_all(src, BusLine)))
        num_stops = len(list(self.get_all(src, BusStop)))
        colour = ERROR if (num_lines == 0 and not src.is_warp_source()) or num_stops == 0 else RESULT
        self.print_report(src, colour, f"has {num_lines} lines and {num_stops} stops")


class BusLine(gt.BusLine, Node, kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (BusCompany, BusStop)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: BusSource,
        *,
        code: str,
        company: BusCompany,
        name: str | None = None,
        colour: str | None = None,
        ref_stop: BusStop | None = None,
    ):
        self = super().new(src, code=code)
        self.connect_one(src, company)
        if name is not None:
            self.name = src.source(name)
        if colour is not None:
            self.colour = src.source(colour)
        if ref_stop is not None:
            self.connect_one(src, ref_stop)
        return self

    @override
    def str_src(self, src: BusSource) -> str:
        code = self.code
        company = self.get_one(src, BusCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, src: BusSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(src, BusCompany).equivalent(src, other.get_one(src, BusCompany))

    @override
    def merge_attrs(self, src: BusSource, other: Self):
        self._merge_sourced(src, other, "name")
        self._merge_sourced(src, other, "colour")

    @override
    def merge_key(self, src: BusSource) -> str:
        return self.code

    @override
    def sanitise_strings(self):
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.colour is not None:
            self.colour.v = str(self.colour.v).strip()

    @override
    def export(self, src: BusSource) -> gt.BusLine:
        return gt.BusLine(**self._as_dict(src))

    @override
    def _as_dict(self, src: BusSource) -> dict:
        return super()._as_dict(src) | {
            "company": self.get_one_id(src, BusCompany),
            "ref_stop": self.get_one_id(src, BusStop),
        }

    @override
    def ref(self, src: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusLine, code=self.code, company=self.get_one(src, BusCompany).name)

    @override
    def report(self, src: BusSource):
        num_stops = len(
            [
                stn
                for stn in self.get_one(src, BusCompany).get_all(src, BusStop)
                if any(
                    conn.v.line.refs(src, self)
                    for node in stn.get_all(src, BusStop, BusConnection)
                    for conn in stn.get_edges(src, node, BusConnection)
                )
            ]
        )
        colour = ERROR if num_stops == 0 else RESULT
        self.print_report(src, colour, f"has {num_stops} stops")


class BusStop(gt.BusStop, LocatedNode, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (BusStop, BusLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (BusCompany,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: BusSource,
        *,
        codes: set[str],
        company: BusCompany,
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
    def str_src(self, src: BusSource) -> str:
        codes = "/".join(self.codes)
        code = codes if (name := self.name) is None or name.v in codes else f"{name.v} ({codes})"
        company = self.get_one(src, BusCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, src: BusSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(src, BusCompany).equivalent(
            src, other.get_one(src, BusCompany)
        )

    @override
    def merge_attrs(self, src: BusSource, other: Self):
        super().merge_attrs(src, other)
        self.codes.update(other.codes)
        self._merge_sourced(src, other, "name")

    @override
    def merge_key(self, src: BusSource) -> str:
        return self.get_one(src, BusCompany).name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.codes = {str(a).strip() for a in self.codes}
        if self.name is not None:
            self.name.v = str(self.name.v).strip()

    @override
    def export(self, src: BusSource) -> gt.BusStop:
        return gt.BusStop(
            **self._as_dict(src),
        )

    @override
    def _as_dict(self, src: BusSource) -> dict:
        return super()._as_dict(src) | {
            "company": self.get_one_id(src, BusCompany),
            "connections": {
                node.i: [a.export(src) for a in self.get_edges(src, node, BusConnection)]
                for node in self.get_all(src, BusStop)
            },
        }

    @override
    def ref(self, src: BusSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(BusStop, codes=self.codes, company=self.get_one(src, BusCompany).name)

    @override
    def report(self, src: BusSource):
        super().report(src)
        num_connections = len(list(self.get_all(src, BusStop, BusConnection)))
        if num_connections == 0:
            self.print_report(src, ERROR, "has no connections")


class BusConnection(Connection[BusLine]):
    pass


class BusLineBuilder(LineBuilder[BusLine, BusStop]):
    CnT = BusConnection
