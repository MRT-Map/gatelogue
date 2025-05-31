from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self, override

import rich

import gatelogue_types as gt
from gatelogue_aggregator.logging import RESULT, ERROR

from gatelogue_aggregator.types.edge.connections import Connection
from gatelogue_aggregator.types.edge.line_builder import LineBuilder
from gatelogue_aggregator.types.node.base import LocatedNode, Node, NodeRef
from gatelogue_aggregator.types.source import Source

if TYPE_CHECKING:
    from collections.abc import Iterable


class SeaSource(Source):
    pass


class SeaCompany(gt.SeaCompany, Node, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (SeaLine, SeaStop)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: SeaSource,
        *,
        name: str,
        lines: Iterable[SeaLine] | None = None,
        stops: Iterable[SeaStop] | None = None,
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
    def str_src(self, src: SeaSource) -> str:
        return self.name

    @override
    def equivalent(self, src: SeaSource, other: Self) -> bool:
        return self.name == other.name

    @override
    def merge_attrs(self, src: SeaSource, other: Self):
        self.local = self.local or other.local

    @override
    def merge_key(self, src: SeaSource) -> str:
        return self.name

    @override
    def sanitise_strings(self):
        self.name = str(self.name).strip()

    @override
    def export(self, src: SeaSource) -> gt.SeaCompany:
        return gt.SeaCompany(
            **self._as_dict(src),
        )

    @override
    def _as_dict(self, src: SeaSource) -> dict:
        return super()._as_dict(src) | {
            "lines": self.get_all_id(src, SeaLine),
            "stops": self.get_all_id(src, SeaStop),
        }

    @override
    def ref(self, src: SeaSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(SeaCompany, name=self.name)

    @override
    def report(self, src: SeaSource):
        num_lines = len(list(self.get_all(src, SeaLine)))
        num_stops = len(list(self.get_all(src, SeaStop)))
        colour = ERROR if num_lines == 0 or num_stops == 0 else RESULT
        rich.print(colour + type(self).__name__ + " " + self.str_src(src) + f" has {num_lines} lines and {num_stops} stops")


class SeaLine(gt.SeaLine, Node, kw_only=True, tag=True):
    acceptable_single_node_types: ClassVar = lambda: (SeaCompany, SeaStop)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: SeaSource,
        *,
        code: str,
        company: SeaCompany,
        name: str | None = None,
        colour: str | None = None,
        mode: gt.SeaMode | None = None,
        ref_stop: SeaStop | None = None,
    ):
        self = super().new(src, code=code)
        self.connect_one(src, company)
        if name is not None:
            self.name = src.source(name)
        if colour is not None:
            self.colour = src.source(colour)
        if mode is not None:
            self.mode = src.source(mode)
        if ref_stop is not None:
            self.connect_one(src, ref_stop)
        return self

    @override
    def str_src(self, src: SeaSource) -> str:
        code = self.code
        company = self.get_one(src, SeaCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, src: SeaSource, other: Self) -> bool:
        return self.code == other.code and self.get_one(src, SeaCompany).equivalent(src, other.get_one(src, SeaCompany))

    @override
    def merge_attrs(self, src: SeaSource, other: Self):
        self._merge_sourced(src, other, "name")
        self._merge_sourced(src, other, "colour")
        self._merge_sourced(src, other, "mode")

    @override
    def merge_key(self, src: SeaSource) -> str:
        return self.code

    @override
    def sanitise_strings(self):
        self.code = str(self.code).strip()
        if self.name is not None:
            self.name.v = str(self.name.v).strip()
        if self.colour is not None:
            self.colour.v = str(self.colour.v).strip()

    @override
    def export(self, src: SeaSource) -> gt.SeaLine:
        return gt.SeaLine(
            **self._as_dict(src),
        )

    @override
    def _as_dict(self, src: SeaSource) -> dict:
        return super()._as_dict(src) | {
            "company": self.get_one_id(src, SeaCompany),
            "ref_stop": self.get_one_id(src, SeaStop),
        }

    @override
    def ref(self, src: SeaSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(SeaLine, code=self.code, company=self.get_one(src, SeaCompany).name)

    @override
    def report(self, src: SeaSource):
        num_stops = len([stn for stn in self.get_one(src, SeaCompany).get_all(src, SeaStop) if any(
            conn.v.line.refs(src, self)
            for node in stn.get_all(src, SeaStop, SeaConnection)
            for conn in stn.get_edges(src, node, SeaConnection)
        )])
        colour = ERROR if num_stops == 0 else RESULT
        rich.print(colour + type(self).__name__ + " " + self.str_src(src) + f" has {num_stops} stops")


class SeaStop(gt.SeaStop, LocatedNode, kw_only=True, tag=True):
    acceptable_list_node_types: ClassVar = lambda: (SeaStop, SeaLine, LocatedNode)
    acceptable_single_node_types: ClassVar = lambda: (SeaCompany,)

    # noinspection PyMethodOverriding
    @classmethod
    def new(
        cls,
        src: SeaSource,
        *,
        codes: set[str],
        company: SeaCompany,
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
    def str_src(self, src: SeaSource) -> str:
        codes = "/".join(self.codes); code = codes if (name := self.name) is None or name.v in codes else f"{name.v} ({codes})"
        company = self.get_one(src, SeaCompany).name
        return f"{company} {code}"

    @override
    def equivalent(self, src: SeaSource, other: Self) -> bool:
        return len(self.codes.intersection(other.codes)) != 0 and self.get_one(src, SeaCompany).equivalent(
            src, other.get_one(src, SeaCompany)
        )

    @override
    def merge_attrs(self, src: SeaSource, other: Self):
        super().merge_attrs(src, other)
        self.codes.update(other.codes)
        self._merge_sourced(src, other, "name")

    @override
    def merge_key(self, src: SeaSource) -> str:
        return self.get_one(src, SeaCompany).name

    @override
    def sanitise_strings(self):
        super().sanitise_strings()
        self.codes = {str(a).strip() for a in self.codes}
        if self.name is not None:
            self.name.v = str(self.name.v).strip()

    @override
    def export(self, src: SeaSource) -> gt.SeaStop:
        return gt.SeaStop(
            **self._as_dict(src),
        )

    @override
    def _as_dict(self, src: SeaSource) -> dict:
        return super()._as_dict(src) | {
            "company": self.get_one_id(src, SeaCompany),
            "connections": {
                node.i: [a.export(src) for a in self.get_edges(src, node, SeaConnection)]
                for node in self.get_all(src, SeaStop)
            },
        }

    @override
    def ref(self, src: SeaSource) -> NodeRef[Self]:
        self.sanitise_strings()
        return NodeRef(SeaStop, codes=self.codes, company=self.get_one(src, SeaCompany).name)

    @override
    def report(self, src: SeaSource):
        super().report(src)
        num_connections = len(list(self.get_all(src, SeaStop, SeaConnection)))
        if num_connections == 0:
            rich.print(ERROR + type(self).__name__ + " " + self.str_src(src) + f" has no connections")


class SeaConnection(Connection[SeaLine]):
    pass


class SeaLineBuilder(LineBuilder[SeaLine, SeaStop]):
    CnT = SeaConnection
