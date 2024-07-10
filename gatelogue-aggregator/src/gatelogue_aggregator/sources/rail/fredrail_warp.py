import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailSource


class FredRailWarp(RailSource):
    name = "MRT Warp API (Rail, Fred Rail)"
    priority = 1

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="Fred Rail")

        names = []
        for warp in warps(uuid.UUID("8ebc5173-3df2-450c-92a3-e13063409a24"), config):
            if not warp["name"].startswith("FR"):
                continue
            if (
                match := re.search(
                    r"(?i)(?:This is|The next (?:and last )?stop is) (?!a|the)([^.]*)\.", warp["welcomeMessage"]
                )
            ) is None:
                # rich.print(ERROR+"Unknown warp message format:", warp['welcomeMessage'])
                continue
            name = match.group(1)
            name = {
                "Segville International": "Segville International Airport",
                "Zaquar Onika T": "Zaquar Onika T. Maraj Station",
                "UCWTIA West Station": "UCWTIA",
                "Boston Clapham Station": "Boston Clapham Junction",
                "Sealane": "Sealane New Forest Station",
                "Bakersville": "Bakersville Grand Central",
            }.get(name, name)
            print(name)
            if name in names:
                continue
            self.rail_station(
                codes={name},
                company=company,
                world="New",
                coordinates=(warp["x"], warp["z"]),
            )
            names.append(name)
        self.save_to_cache(config, self.g)
