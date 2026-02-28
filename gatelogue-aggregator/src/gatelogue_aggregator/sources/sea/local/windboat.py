from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.yaml2source import SeaYaml2Source, YamlLine, YamlRoute

if TYPE_CHECKING:
    import gatelogue_types as gt

    from gatelogue_aggregator.sources.line_builder import SeaLineBuilder


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
            stations_left = []
            if line_node.code == "KN" and station.name in ("Anseijima", "Triangle Archipelago"):
                stations_left.append(self.stop(codes={"Minami-kengiguntō"}, company=line_node.company))
            elif line_node.code == "HE" and station.name == "Tristan de Cunha":
                stations_left.append(self.stop(codes={"Rose Island"}, company=line_node.company))
            elif i - 2 >= 0:
                stations_left.append(builder.station_list[i - 2])
            for station_left in stations_left:
                dock_left = self.dock(code=None, stop=station_left)
                self.connection(line=line_node, from_=dock, to=dock_left, direction=None)

            stations_right = []
            if line_node.code == "KN" and station.name == "Minami-kengiguntō":
                stations_right.append(self.stop(codes={"Anseijima"}, company=line_node.company))
                stations_right.append(self.stop(codes={"Triangle Archipelago"}, company=line_node.company))
            elif line_node.code == "HE" and station.name == "Rose Island":
                stations_right.append(self.stop(codes={"Tristan de Cunha"}, company=line_node.company))
            elif i + 2 < len(builder.station_list):
                stations_right.append(builder.station_list[i - 2])
            for station_right in stations_right:
                dock_right = self.dock(code=None, stop=station_right)
                self.connection(line=line_node, from_=dock, to=dock_right, direction=None)
