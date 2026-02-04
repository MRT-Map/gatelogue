from __future__ import annotations

from pathlib import Path
from typing import Literal

import gatelogue_types as gt

from gatelogue_aggregator.sources.line_builder import SeaLineBuilder
from gatelogue_aggregator.sources.yaml2source import SeaYaml2Source, YamlLine, YamlRoute


class Windboat(SeaYaml2Source):
    name = "Gatelogue (Sea, Windboat)"
    file_path = Path(__file__).parent / "windboat.yaml"

    def routing(
        self,
        line_node: gt.SeaLine,
        builder: SeaLineBuilder,
        line_yaml: YamlLine,
        route_yaml: YamlRoute,
        cp: SeaYaml2Source._ConnectParams,
    ):
        cp["forward_direction"] = cp["backward_direction"] = None
        builder.connect(**cp)
        for i in range(len(builder.station_list)):
            station = builder.station_list[i]
            dock = next(station.docks)
            station_left = []
            if line_node.code == "KN" and station.name in ("Anseijima", "Triangle Archipelago"):
                station_left.append(self.stop(codes={"Minami-kengiguntō"}, company=line_node.company))
            elif line_node.code == "HE" and station.name == "Tristan de Cunha":
                station_left.append(self.stop(codes={"Rose Island"}, company=line_node.company))
            elif i - 2 >= 0:
                station_left.append(builder.station_list[i - 2])
            for station_left in station_left:
                dock_left = self.dock(code=None, stop=station_left)
                self.connection(line=line_node, from_=dock, to=dock_left, direction=None)

            station_right = []
            if line_node.code == "KN" and station.name == "Minami-kengiguntō":
                station_right.append(self.stop(codes={"Anseijima"}, company=line_node.company))
                station_right.append(self.stop(codes={"Triangle Archipelago"}, company=line_node.company))
            elif line_node.code == "HE" and station.name == "Rose Island":
                station_right.append(self.stop(codes={"Tristan de Cunha"}, company=line_node.company))
            elif i + 2 < len(builder.station_list):
                station_right.append(builder.station_list[i - 2])
            for station_right in station_right:
                dock_right = self.dock(code=None, stop=station_right)
                self.connection(line=line_node, from_=dock, to=dock_right, direction=None)
