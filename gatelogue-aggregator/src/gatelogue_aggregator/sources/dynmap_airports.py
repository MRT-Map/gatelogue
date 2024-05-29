import msgspec.json
import requests
import rich.status

from gatelogue_aggregator.types.base import Source, Sourced
from gatelogue_aggregator.types.context import AirContext


class DynmapAirports(AirContext, Source):
    name = "MRT Dynmap"

    def __init__(self):
        super().__init__()
        status = rich.status.Status("Downloading JSON")
        status.start()
        json = requests.get("https://dynmap.minecartrapidtransit.net/main/tiles/_markers_/marker_new.json").json()["sets"]["airports"]["markers"]
        status.stop()
        rich.print("[green]Downloaded")

        for k, v in json.items():
            self.get_airport(code=k, coordinates=Sourced((v['x'], v['z'])).source(self))

        self.update()
        rich.print(self.dict())
