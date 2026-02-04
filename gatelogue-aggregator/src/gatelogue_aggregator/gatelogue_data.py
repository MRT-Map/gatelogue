from __future__ import annotations

import difflib
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import gatelogue_types as gt
import msgspec
import rich
from gatelogue_types import node

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.logging import ERROR, INFO1, INFO2, INFO3, RESULT, track
from gatelogue_aggregator.report import report
from gatelogue_aggregator.source import Source

if TYPE_CHECKING:
    from collections.abc import Container, Iterable


class GatelogueData:
    def __init__(self, config: Config, sources: Iterable[type[Source]], database=":memory:"):
        self.config = config
        self._build_sources(sources, database)

        prev_length: int | None = None
        for pass_ in range(1, 10):
            self._merge_equivalent_nodes(pass_)
            self._merge_airports_with_unknown_code(pass_)
            self._merge_gates_without_code()

            if len(self.gd) == prev_length:
                break
            prev_length = len(self.gd)

        self._update_flight_mode()
        self._dedup_airport_names()
        self._update_gate_size()
        self._proximity()
        self._shared_facility()

    def _build_sources(self, sources: Iterable[type[Source]], database=":memory:"):
        for i, source in enumerate(sources):
            source.priority = i
        self.gd = gt.GD.create([a.__name__ for a in sources], database)

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            source_instances: list[Source] = list(executor.map(lambda s: s(self.config, self.gd.conn), sources))

        for source in track(source_instances, INFO1, description="Building sources"):
            source.build(self.config)
            source.report()

    def _merge_equivalent_nodes(self, pass_: int):
        merged: set[int] = set()
        for n in track(
            self.gd.nodes(),
            INFO2,
            description=f"Merging equivalent nodes (pass {pass_})",
        ):
            if n.i in merged:
                continue
            for equiv in n.equivalent_nodes():
                if n.i == equiv.i:
                    continue
                n.merge(equiv, warn_fn=lambda msg: rich.print(ERROR + msg))
                merged.add(equiv.i)

    def _merge_airports_with_unknown_code(self, pass_: int):
        name2i = {
            name: i
            for name, i in self.gd.conn.execute(
                "SELECT name, AirAirport.i FROM AirAirport "
                "INNER JOIN AirAirportNames on AirAirport.i = AirAirport.i = AirAirportNames.i"
            ).fetchall()
        }

        for n in track(
            (gt.AirAirport(self.gd.conn, i) for i in self.gd.conn.execute("SELECT i FROM AirAirport WHERE code == ''")),
            INFO2,
            description=f"Merging airports (pass {pass_})",
        ):
            best_name = next(
                iter(difflib.get_close_matches(next(iter(n.names)), name2i.keys(), 1, 0.0)),
                None,
            )
            if best_name is not None:
                equiv = gt.AirAirport(self.gd.conn, name2i[best_name])
                rich.print(
                    RESULT
                    + f"AirAirport of name `{n.names}` found code `{equiv.code}` with similar name `{equiv.names}`"
                )
                n.code = equiv.code
                equiv.merge(n, warn_fn=lambda msg: rich.print(ERROR + msg))

    def _update_flight_mode(self):
        for n in track(
            (gt.AirFlight(self.gd.conn, i) for i in self.gd.conn.execute("SELECT i FROM AirFlight WHERE mode IS NULL")),
            INFO2,
            description="Updating AirFlight `mode` field",
        ):
            size: set[str] = n.from_.size | n.to.size
            sources = lambda: {
                s
                for (s,) in self.gd.conn.execute(
                    "SELECT DISTINCT source FROM AirGateSource WHERE (i = :from_ OR i = :to) AND size = true",
                    dict(from_=n.from_.i, to=n.to.i),
                ).fetchall()
            }
            if size == {"SP"}:
                n.mode = sources(), "seaplane"
            elif size == {"H"}:
                n.mode = sources(), "helicopter"

    def _dedup_airport_names(self):
        for n in track(self.gd.nodes(gt.AirAirport), INFO2, description="Deduplicating AirAirport `name` field"):
            names: set[str] = n.names
            ok_names = set()
            for name in sorted(names, key=len, reverse=True):
                if any(
                    (
                        name in existing
                        or sorted(re.sub(r"[^\w\s]", "", name).split())
                        == sorted(re.sub(r"[^\w\s]", "", existing).split())
                    )
                    for existing in ok_names
                ):
                    cur = self.gd.conn.cursor()
                    cur.execute(
                        "DELETE FROM AirAirportNamesSource WHERE i = :i AND name = :name", dict(i=n.i, name=name)
                    )
                    cur.execute("DELETE FROM AirAirportNames WHERE i = :i AND name = :name", dict(i=n.i, name=name))
                else:
                    ok_names.add(name)

    def _merge_gates_without_code(self):
        for airport in track(self.gd.nodes(gt.AirAirport), INFO2, description="Merging AirGates without code"):
            airline2gate = {
                airline: gt.AirGate(self.gd.conn, gate)
                for airline, gate in self.gd.conn.execute(
                    "SELECT airline, max(i) FROM AirGate "
                    "WHERE airport = :i AND code IS NOT NULL GROUP BY airline HAVING count(i) = 1",
                    dict(i=airport.i),
                ).fetchall()
            }
            for n in (
                gt.AirGate(self.gd.conn, i)
                for i in self.gd.conn.execute(
                    "SELECT i FROM AirGate WHERE airport = :i AND code IS NULL", dict(i=airport.i)
                ).fetchall()
            ):
                if (airline := n.airline) is not None and airline.i in airline2gate:
                    airline2gate[airline.i].merge(n, warn_fn=lambda msg: rich.print(ERROR + msg))

    def _update_gate_size(self):
        for n in track(self.gd.nodes(gt.AirAirport), INFO2, description="Updating AirGate `size` field"):
            if (modes := n.modes) is None:
                continue
            sources = lambda: {
                s
                for (s,) in self.gd.conn.execute(
                    "SELECT DISTINCT source FROM AirAirportModesSource WHERE i = :i", dict(i=n.i)
                ).fetchall()
            }
            if modes == {"seaplane"}:
                for gate in n.gates:
                    gate.size = sources(), "SP"
            elif modes == {"helicopter"}:
                for gate in n.gates:
                    gate.size = sources(), "H"

    def _isolated_nodes(self, nodes: set[int]) -> list[set[int]]:
        components = [set()]
        processed = set()
        queue = set()
        while len(nodes) != 0:
            if len(queue) == 0:
                components.append(set())
                n = next(iter(nodes))
            else:
                n = next(iter(queue))
                queue.remove(n)
            components[-1].add(n)
            processed.add(n)
            nodes.remove(n)
            queue |= {a for a in gt.LocatedNode(self.gd.conn, n)._nodes_in_proximity}
            queue -= processed
        components.remove(max(components, key=len))
        return components

    def _proximity(self):
        nodes = {
            gt.LocatedNode(self.gd.conn, i)
            for (i,) in self.gd.conn.execute(
                "SELECT i FROM NodeLocation WHERE world IS NOT NULL AND world != 'Space' AND x IS NOT NULL and y IS NOT NULL"
            )
        }
        processed = []
        for n in track(nodes, INFO2, description="Linking close nodes", nonlinear=True):
            for existing in processed:
                if existing.world != n.world:
                    continue
                x1, y1 = existing.coordinates
                x2, y2 = n.coordinates
                dist_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2
                threshold = 500**2 if isinstance(existing, gt.AirAirport) or isinstance(n, gt.AirAirport) else 250**2
                if dist_sq < threshold:
                    srcs = {
                        s
                        for (s,) in self.gd.conn.execute(
                            "SELECT DISTINCT source FROM NodeLocationSource "
                            "WHERE (i = :i1 OR i = :i2) AND (world IS true OR coordinates IS TRUE)",
                            dict(i1=n.i, i2=existing.i),
                        )
                    }
                    gt.Proximity.create(self.gd.conn, srcs, node1=n, node2=existing, distance=dist_sq**0.5)
            processed.append(n)

        def dist_sq_fn(n_: gt.LocatedNode, this_: gt.LocatedNode, others: Container[int]):
            if n_.world != this_.world or n_.i in others:
                return float("inf")
            nx, ny = n_.coordinates
            tx, ty = this_.coordinates
            return (nx - tx) ** 2 + (ny - ty) ** 2

        for pass_ in range(1, 10):
            isolated = self._isolated_nodes({n.i for n in nodes})
            if len(isolated) == 0:
                break
            for component in track(
                isolated,
                INFO2,
                description=f"Ensuring all located nodes are connected (pass {pass_})",
            ):
                for this_i in component:
                    this = gt.LocatedNode(self.gd.conn, this_i)
                    nearest = min(nodes, key=lambda nr: dist_sq_fn(nr, this, component))
                    if nearest.i in this._nodes_in_proximity:
                        continue
                    srcs = {
                        s
                        for (s,) in self.gd.conn.execute(
                            "SELECT DISTINCT source FROM NodeLocationSource "
                            "WHERE (i = :i1 OR i = :i2) AND (world IS true OR coordinates IS TRUE)",
                            dict(i1=this.i, i2=nearest.i),
                        )
                    }
                    gt.Proximity.create(
                        self.gd.conn,
                        srcs,
                        node1=this,
                        node2=nearest,
                        distance=dist_sq_fn(nearest, this, component) ** 0.5,
                    )

    def _shared_facility(self):
        class Yaml(msgspec.Struct):
            c1: str
            c2: str
            s1: str = ""
            s2: str = ""
            code1: str | None = None
            code2: str | None = None
            m1: Literal["Bus", "Rail", "Sea"] = "Rail"
            m2: Literal["Bus", "Rail", "Sea"] = "Rail"

        nonexistent_companies = set()

        def get_company(mode: str, name: str) -> gt.BusCompany | gt.RailCompany | gt.SeaCompany | None:
            if name in nonexistent_companies:
                return None
            company = None
            match mode:
                case "Bus":
                    if (
                        result := self.gd.conn.execute(
                            "SELECT i FROM BusCompany WHERE name = :name", dict(name=name)
                        ).fetchone()
                    ) is not None:
                        company = gt.BusCompany(self.gd.conn, result[0])
                case "Rail":
                    if (
                        result := self.gd.conn.execute(
                            "SELECT i FROM RailCompany WHERE name = :name", dict(name=name)
                        ).fetchone()
                    ) is not None:
                        company = gt.RailCompany(self.gd.conn, result[0])
                case "Sea":
                    if (
                        result := self.gd.conn.execute(
                            "SELECT i FROM SeaCompany WHERE name = :name", dict(name=name)
                        ).fetchone()
                    ) is not None:
                        company = gt.SeaCompany(self.gd.conn, result[0])
                case _:
                    raise ValueError(mode)
            if company is None:
                rich.print(ERROR + f"Company {name} does not exist")
                nonexistent_companies.add(name)
            return company

        def get_stop(
            mode: str, company: gt.BusCompany | gt.RailCompany | gt.SeaCompany, name: str, code: str | None = None
        ) -> gt.BusStop | gt.RailStation | gt.SeaStop:
            stop = None
            match mode:
                case "Bus":
                    if code is None:
                        result = self.gd.conn.execute(
                            "SELECT i FROM BusStop WHERE name = :name AND company = :ci", dict(name=name, ci=company.i)
                        ).fetchone()
                    else:
                        result = self.gd.conn.execute(
                            "SELECT BusStop.i from BusStop "
                            "LEFT JOIN BusStopCodes on BusStop.i = BusStopCodes.i "
                            "WHERE code = :code AND company = :ci",
                            dict(code=code, ci=company.i),
                        ).fetchone()
                    if result is not None:
                        stop = gt.BusStop(self.gd.conn, result[0])
                case "Rail":
                    if code is None:
                        result = self.gd.conn.execute(
                            "SELECT i FROM RailStation WHERE name = :name AND company = :ci",
                            dict(name=name, ci=company.i),
                        ).fetchone()
                    else:
                        result = self.gd.conn.execute(
                            "SELECT RailStation.i from RailStation "
                            "LEFT JOIN RailStationCodes on RailStation.i = RailStationCodes.i "
                            "WHERE code = :code AND company = :ci",
                            dict(code=code, ci=company.i),
                        ).fetchone()
                    if result is not None:
                        stop = gt.RailStation(self.gd.conn, result[0])
                case "Sea":
                    if code is None:
                        result = self.gd.conn.execute(
                            "SELECT i FROM SeaStop WHERE name = :name AND company = :ci", dict(name=name, ci=company.i)
                        ).fetchone()
                    else:
                        result = self.gd.conn.execute(
                            "SELECT SeaStop.i from SeaStop "
                            "LEFT JOIN SeaStopCodes on SeaStop.i = SeaStopCodes.i "
                            "WHERE code = :code AND company = :ci",
                            dict(code=code, ci=company.i),
                        ).fetchone()
                    if result is not None:
                        stop = gt.SeaStop(self.gd.conn, result[0])
                case _:
                    raise ValueError(mode)
            if stop is None:
                rich.print(ERROR + f"{company.name} {name} does not exist")
            return stop

        with (Path(__file__).parent / "sources" / "shared_facilities.yaml").open() as f:
            file = msgspec.yaml.decode(f.read(), type=list[Yaml])

        for entry in file:
            if (company1 := get_company(entry.m1, entry.c1)) is None:
                continue
            if (company2 := get_company(entry.m2, entry.c2)) is None:
                continue
            if (stop1 := get_stop(entry.m1, company1, entry.s1, entry.code1)) is None:
                continue
            if (stop2 := get_stop(entry.m2, company2, entry.s2, entry.code2)) is None:
                continue

            gt.SharedFacility.create(self.gd.conn, node1=stop1, node2=stop2)

    def report(self):
        rich.print(INFO1 + "Below is a final report of all nodes collected")
        for node in self.gd.nodes():
            report(node)
        rich.print(INFO1 + "End of report")

    def graph(self, path: Path):
        g = self.g.copy()
        for i, (u, v, data) in g.edge_index_map().items():
            g.update_edge_by_index(i, (u, v, data))

        def replace(s):
            return s.replace('"', '\\"')

        def node_fn(node: Node):
            d = {
                "style": "filled",
                "tooltip": replace(Node.str_src(node, self)),
                "label": replace(node.str_src(self)),
            }
            for ty, col in (
                (AirFlight, "#ff8080"),
                (AirAirport, "#8080ff"),
                (AirAirline, "#ffff80"),
                (AirGate, "#80ff80"),
                (RailCompany, "#ffff80"),
                (RailLine, "#ff8080"),
                (RailStation, "#8080ff"),
                (SeaCompany, "#ffff80"),
                (SeaLine, "#ff8080"),
                (SeaStop, "#8080ff"),
                (BusCompany, "#ffff80"),
                (BusLine, "#ff8080"),
                (BusStop, "#8080ff"),
                (Town, "#aaaaaa"),
                (SpawnWarp, "#aaaaaa"),
            ):
                if isinstance(node, ty):
                    d["fillcolor"] = '"' + col + '"'
                    break
            return d

        def edge_fn(edge):
            u = g[edge[0]]
            v = g[edge[1]]
            edge = edge[2]
            edge_data = edge.v if isinstance(edge, Sourced) else edge
            d = {}
            if edge_data is None:
                d["tooltip"] = replace(f"({u.str_src(self)} -- {v.str_src(self)})")
            else:
                d["tooltip"] = replace(f"{edge_data} ({u.str_src(self)} -- {v.str_src(self)})")
            if isinstance(edge_data, node.Proximity):
                d["color"] = '"#ff00ff"'
                return d
            if isinstance(edge_data, SharedFacility):
                d["color"] = '"#008080"'
                return d
            for ty1, ty2, col in (
                (AirAirport, AirGate, "#0000ff"),
                (AirGate, AirFlight, "#00ff00"),
                (AirFlight, AirAirline, "#ff0000"),
                (RailCompany, RailLine, "#ff0000"),
                (RailStation, RailStation, "#0000ff"),
                (SeaCompany, SeaLine, "#ff0000"),
                (SeaStop, SeaStop, "#0000ff"),
                (BusCompany, BusLine, "#ff0000"),
                (BusStop, BusStop, "#0000ff"),
            ):
                if (isinstance(u, ty1) and isinstance(v, ty2)) or (isinstance(u, ty2) and isinstance(v, ty1)):
                    d["color"] = '"' + col + '"'
                    break
            else:
                d["style"] = "invis"
            return d

        # g.to_dot(
        #     node_attr=node_fn,
        #     edge_attr=edge_fn,
        #     graph_attr={"overlap": "prism1000", "outputorder": "edgesfirst"}, filename="test.dot")
        graphviz_draw(
            g,
            node_attr_fn=node_fn,
            edge_attr_fn=edge_fn,
            graph_attr={"overlap": "prism1000", "outputorder": "edgesfirst"},
            filename=str(path),
            image_type="svg",
            method="sfdp",
        )
