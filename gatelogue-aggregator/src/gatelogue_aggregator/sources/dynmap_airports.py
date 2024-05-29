import requests
import rich.status

from gatelogue_aggregator.types.base import Source, Sourced
from gatelogue_aggregator.types.context import AirContext


class DynmapAirports(AirContext, Source):
    name = "MRT Dynmap"

    def __init__(self, timeout: int = 60):
        AirContext.__init__(self)
        Source.__init__(self)

        status = rich.status.Status("Downloading JSON")
        status.start()
        json = requests.get(
            "https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json", timeout=timeout
        ).json()["sets"]["airports"]["markers"]
        status.stop()
        rich.print("[green]Downloaded")

        for k, v in json.items():
            self.get_airport(code=k, coordinates=Sourced((v["x"], v["z"])).source(self))

        self.update()
