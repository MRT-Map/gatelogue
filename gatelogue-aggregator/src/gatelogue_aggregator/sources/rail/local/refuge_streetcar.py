from __future__ import annotations

from pathlib import Path

from gatelogue_aggregator.sources.line_builder import RailLineBuilder, BusLineBuilder, SeaLineBuilder
from gatelogue_aggregator.sources.yaml2source import Yaml2Source, YamlLine, RailYaml2Source, YamlRoute
import gatelogue_types as gt


class RefugeStreetcar(RailYaml2Source):
    name = "Gatelogue (Rail, Refuge Streetcar)"
    file_path = Path(__file__).parent / "refuge_streetcar.yaml"

    def routing(
        self,
        line_node: gt.RailLine,
        builder: RailLineBuilder,
        line_yaml: YamlLine,
        route_yaml: YamlRoute,
        cp: RailYaml2Source._ConnectParams,
    ):
        if line_node.code == "North/South Loop":
            builder.connect_to("West Train Station", **cp)

            cp["forward_direction"] = "Anticlockwise"
            builder.connect(until="West Train Station", **cp)

            cp["forward_direction"] = "Southbound"
            cp["backward_direction"] = "Northbound"
            builder.connect(until="South Hill", **cp)

            cp["forward_direction"] = "Anticlockwise"
            builder.connect(**cp)

            builder.connect_to("South Hill", **cp)
        else:
            cp["forward_direction"] = "Clockwise"
            cp["backward_direction"] = "Anticlockwise"
            builder.connect_circle(**cp)
