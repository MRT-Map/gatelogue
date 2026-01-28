from collections.abc import Container

import gatelogue_types as gt
import rich

from gatelogue_aggregator.logging import ERROR, RESULT


def report(node: gt.Node, prefix: str | None = None, ignore: Container[type[gt.Node]] = None):
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
    rich.print(colour + string)
