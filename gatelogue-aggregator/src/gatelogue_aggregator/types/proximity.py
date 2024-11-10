from __future__ import annotations

import msgspec
import rustworkx as rx

from gatelogue_aggregator.logging import track, INFO1, INFO2
from gatelogue_aggregator.types.base import BaseContext
from gatelogue_aggregator.types.node.air import AirAirport
from gatelogue_aggregator.types.node.base import LocatedNode, Node
from gatelogue_aggregator.types.node.town import Town


class Proximity(msgspec.Struct):
    distance: int
    """Distance between the two objects in blocks"""


class ProximityContext(BaseContext):
    def update(self):
        processed = []
        for node in track(self.g.nodes(), description=INFO2 + "Linking close nodes", nonlinear=True, remove=False):
            if not isinstance(node, LocatedNode) or node.coordinates is None:
                continue
            node_coordinates = node.coordinates.v
            if node.world is None:
                continue
            for existing, existing_world, existing_coordinates in processed:
                if existing_world != node.world.v:
                    continue
                x1, y1 = existing_coordinates
                x2, y2 = node_coordinates
                dist = (x1 - x2) ** 2 + (y1 - y2) ** 2
                threshold = 500 if isinstance(existing, AirAirport) or isinstance(node, AirAirport) else 250
                if dist < threshold**2:
                    node.connect(
                        self,
                        existing,
                        Proximity(dist**0.5),
                        source=node.world.s | node.coordinates.s | existing.world.s | existing.coordinates.s,
                    )
            processed.append((node, node.world.v, node_coordinates))

        def dist_sq(n: LocatedNode, this: LocatedNode, others: list[LocatedNode]):
            if n.world.v != this.world.v or n in others:
                return float("inf")
            nx, ny = n.coordinates.v
            tx, ty = this.coordinates.v
            return (nx - tx) ** 2 + (ny - ty) ** 2

        for pass_ in range(1, 10):
            components: list[list[Node]] = [[self.g[b] for b in a] for a in rx.connected_components(self.g)]
            components = sorted(components, key=len, reverse=True)
            located_nodes = [a for a in self.g.nodes() if isinstance(a, LocatedNode) and a.coordinates is not None]
            isolated = [
                [b for b in a if isinstance(b, LocatedNode) and b.coordinates is not None] for a in components[1:]
            ]
            isolated = [a for a in isolated if len(a) != 0]
            if len(isolated) == 0:
                break
            for component in track(
                isolated, description=INFO2 + f"Ensuring all located nodes are connected (pass {pass_})", remove=False
            ):
                for this in component:
                    nearest = min(located_nodes, key=lambda n: dist_sq(n, this, component))
                    this.connect(
                        self,
                        nearest,
                        Proximity(dist_sq(nearest, this, component) ** 0.5),
                        source=this.world.s | this.coordinates.s | nearest.world.s | nearest.coordinates.s,
                    )
