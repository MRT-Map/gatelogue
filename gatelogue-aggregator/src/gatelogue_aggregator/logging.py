from __future__ import annotations

import contextlib
import os
from collections.abc import Callable, Container, Iterable, Sized
from pathlib import Path
from typing import cast

import pydot
import gatelogue_types as gt
import rich
import rich.progress

PROGRESS: rich.progress.Progress = rich.progress.Progress()
if not os.getenv("NO_PROGRESS_BAR"):
    PROGRESS.start()

INFO1 = "[yellow]"
INFO2 = "[green]  "
INFO3 = "[dim green]    "
RESULT = "[cyan]  "
ERROR = "[bold red]!!! "


def track[T](
    it: Iterable[T], level: str, *, description: str, nonlinear: bool = False, total: int | None = None
) -> Iterable[T]:
    if os.getenv("NO_PROGRESS_BAR"):
        rich.print(level + description)
        yield from it
    else:
        total = total or (((len(it) ** 2) / 2 if nonlinear else len(it)) if isinstance(it, Sized) else None)
        t = PROGRESS.add_task(level + description, total=total)
        for i, o in enumerate(it):
            yield o
            PROGRESS.advance(t, i + 1 if nonlinear else 1)
        PROGRESS.remove_task(t)

    rich.print(level + description + " done")


@contextlib.contextmanager
def progress_bar(level: str, description: str):
    if os.getenv("NO_PROGRESS_BAR"):
        rich.print(level + description)
        yield
    else:
        t = PROGRESS.add_task(level + description, total=None)
        yield t
        PROGRESS.remove_task(t)
    rich.print(level + description + " done")


def report(
    node: gt.Node,
    prefix: str | None = None,
    ignore: Container[type[gt.Node]] = None,
    out_fn: Callable[[str, str], object] | None = None,
):
    out_fn = out_fn or (lambda c, text: rich.print(c + text))
    ignore = ignore or ()
    if type(node) in ignore:
        return
    if prefix is not None:
        prefix += ": "
    else:
        prefix = ""
    string = prefix + str(node) + " "
    colour = RESULT
    if isinstance(node, gt.AirAirline):
        airports = len(list(node.airports))
        gates = len(list(node.gates))
        flights = len(list(node.flights))
        string += f"has {airports} airports, {gates} gates, {flights} flights"
        if (
            (airports == 0 and gt.AirAirport not in ignore)
            or (gates == 0 and gt.AirGate not in ignore)
            or (flights == 0 and gt.AirFlight not in ignore)
        ):
            colour = ERROR
    elif isinstance(node, gt.AirAirport):
        gates = len(list(node.gates))
        string += f"has {gates} gates"
        if gates == 0 and gt.AirGate not in ignore:
            colour = ERROR
    elif isinstance(node, gt.AirFlight):
        string += f"goes between {node.from_} and {node.to}"
    elif isinstance(node, gt.BusCompany):
        lines = len(list(node.lines))
        stops = len(list(node.stops))
        berths = len(list(node.berths))
        string += f"has {lines} lines, {stops} stops, {berths} berths"
        if (
            (lines == 0 and gt.BusLine not in ignore)
            or (stops == 0 and gt.BusStop not in ignore)
            or (berths == 0 and gt.BusBerth not in ignore)
        ):
            colour = ERROR
    elif isinstance(node, gt.BusLine):
        stops = len(list(node.stops))
        berths = len(list(node.berths))
        string += f"has {stops} stops, {berths} berths"
        if (stops == 0 and gt.BusStop not in ignore) or (berths == 0 and gt.BusBerth not in ignore):
            colour = ERROR
    elif isinstance(node, gt.SeaCompany):
        lines = len(list(node.lines))
        stops = len(list(node.stops))
        docks = len(list(node.docks))
        string += f"has {lines} lines, {stops} stops, {docks} docks"
        if (
            (lines == 0 and gt.SeaLine not in ignore)
            or (stops == 0 and gt.SeaStop not in ignore)
            or (docks == 0 and gt.SeaDock not in ignore)
        ):
            colour = ERROR
    elif isinstance(node, gt.SeaLine):
        stops = len(list(node.stops))
        docks = len(list(node.docks))
        string += f"has {stops} stops, {docks} docks"
        if (stops == 0 and gt.SeaStop not in ignore) or (docks == 0 and gt.SeaDock not in ignore):
            colour = ERROR
    elif isinstance(node, gt.RailCompany):
        lines = len(list(node.lines))
        stations = len(list(node.stations))
        platforms = len(list(node.platforms))
        string += f"has {lines} lines, {stations} stations, {platforms} platforms"
        if (
            (lines == 0 and gt.RailLine not in ignore)
            or (stations == 0 and gt.RailStation not in ignore)
            or (platforms == 0 and gt.RailPlatform not in ignore)
        ):
            colour = ERROR
    elif isinstance(node, gt.RailLine):
        stations = len(list(node.stations))
        platforms = len(list(node.platforms))
        string += f"has {stations} stations, {platforms} platforms"
        if (stations == 0 and gt.RailStation not in ignore) or (platforms == 0 and gt.RailPlatform not in ignore):
            colour = ERROR
    else:
        return
    out_fn(colour, string)


def draw_graph(gd: gt.GD) -> bytes:
    g = pydot.Dot(strict=True, overlap="scale", outputorder="edgesfirst")
    for node in track(gd.nodes(), INFO1, description="Adding nodes", total=len(gd)):
        g.add_node(pydot.Node(str(node.i), style="filled", label=str(node)))
    with progress_bar(INFO1, f"Writing graph to svg..."):
        return cast(bytes, g.create("sfdp", "svg"))
    # for i, (u, v, data) in g.edge_index_map().items():
    #     g.update_edge_by_index(i, (u, v, data))
    #
    # def replace(s):
    #     return s.replace('"', '\\"')
    #
    # def node_fn(node: Node):
    #
    #     d = {
    #         "style": "filled",
    #         "tooltip": replace(Node.str_src(node, self)),
    #         "label": replace(node.str_src(self)),
    #     }
    #     for ty, col in (
    #             (AirFlight, "#ff8080"),
    #             (AirAirport, "#8080ff"),
    #             (AirAirline, "#ffff80"),
    #             (AirGate, "#80ff80"),
    #             (RailCompany, "#ffff80"),
    #             (RailLine, "#ff8080"),
    #             (RailStation, "#8080ff"),
    #             (SeaCompany, "#ffff80"),
    #             (SeaLine, "#ff8080"),
    #             (SeaStop, "#8080ff"),
    #             (BusCompany, "#ffff80"),
    #             (BusLine, "#ff8080"),
    #             (BusStop, "#8080ff"),
    #             (Town, "#aaaaaa"),
    #             (SpawnWarp, "#aaaaaa"),
    #     ):
    #         if isinstance(node, ty):
    #             d["fillcolor"] = '"' + col + '"'
    #             break
    #     return d
    #
    # def edge_fn(edge):
    #     u = g[edge[0]]
    #     v = g[edge[1]]
    #     edge = edge[2]
    #     edge_data = edge.v if isinstance(edge, Sourced) else edge
    #     d = {}
    #     if edge_data is None:
    #         d["tooltip"] = replace(f"({u.str_src(self)} -- {v.str_src(self)})")
    #     else:
    #         d["tooltip"] = replace(f"{edge_data} ({u.str_src(self)} -- {v.str_src(self)})")
    #     if isinstance(edge_data, node.Proximity):
    #         d["color"] = '"#ff00ff"'
    #         return d
    #     if isinstance(edge_data, SharedFacility):
    #         d["color"] = '"#008080"'
    #         return d
    #     for ty1, ty2, col in (
    #             (AirAirport, AirGate, "#0000ff"),
    #             (AirGate, AirFlight, "#00ff00"),
    #             (AirFlight, AirAirline, "#ff0000"),
    #             (RailCompany, RailLine, "#ff0000"),
    #             (RailStation, RailStation, "#0000ff"),
    #             (SeaCompany, SeaLine, "#ff0000"),
    #             (SeaStop, SeaStop, "#0000ff"),
    #             (BusCompany, BusLine, "#ff0000"),
    #             (BusStop, BusStop, "#0000ff"),
    #     ):
    #         if (isinstance(u, ty1) and isinstance(v, ty2)) or (isinstance(u, ty2) and isinstance(v, ty1)):
    #             d["color"] = '"' + col + '"'
    #             break
    #     else:
    #         d["style"] = "invis"
    #     return d
    #
    # # g.to_dot(
    # #     node_attr=node_fn,
    # #     edge_attr=edge_fn,
    # #     graph_attr={"overlap": "prism1000", "outputorder": "edgesfirst"}, filename="test.dot")
    # graphviz_draw(
    #     g,
    #     node_attr_fn=node_fn,
    #     edge_attr_fn=edge_fn,
    #     graph_attr={"overlap": "prism1000", "outputorder": "edgesfirst"},
    #     filename=str(path),
    #     image_type="svg",
    #     method="sfdp",
    # )
