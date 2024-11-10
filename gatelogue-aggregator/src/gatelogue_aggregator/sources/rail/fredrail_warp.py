from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailCompany, RailSource, RailStation
from gatelogue_aggregator.types.source import Source


class FredRailWarp(RailSource):
    name = "Hardcode (Rail, Fred Rail)"
    priority = 0

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="Fred Rail")

        for station, x, z in (
            ("Bakersville Grand Central", -366, -4180),
            ("Westchester Junction", -590, -3588),
            ("New Risima", -590, -3251),
            ("Xilia", -1497, -651),
            ("Formosa", -1982, -242),
            ("UCWTIA", -1706, 939),
            ("Segville International Airport", -1053, 2685),
            ("Matheson Swamps", 2136, 4425),
            ("Astoria", 3199, 7720),
            ("Fort Yaxier Central", 3567, 9400),
            ("Fort Yaxier Penn", 3469, 10133),
            ("Utopia", -1801, 3724),
            ("Tranquil Forest Central", 9601, 7646),
            ("Wythern", 6149, 6825),
            ("Richville", 12513, 6751),
            ("Utopia AFK", -2346, 3414),
            ("Whiteley Turing Square", -1540, 8076),
            ("Kolpino", -3962, 3743),
            ("Espil", -5745, 2048),
            ("Kings Cross Railway Terminal", -8135, 7619),
            ("Matheson", 356, 4473),
            ("Far Matheson", 1832, 4473),
            ("San Dzobiak", 2103, 3308),
            ("Siletz", 2544, 2995),
            ("Dabecco", 2595, 2511),
            ("Lochminehead", 2369, 857),
            ("Tung Wan Halt", 1799, 13985),
            ("Tung Wan Transfer", 1803, 13692),
            ("Palo Alto", 2923, 13791),
            ("Concord", 3609, 15298),
            ("Redwood Ferry", 4002, 16108),
            ("Victoria Ferry", 5572, 16161),
            ("Victoria Preston", 5351, 16704),
            ("Veldberg", 6223, 17741),
            ("Princeton Junction", 6965, 19707),
            ("Rattlerville Central", 5596, 20814),
            ("New Haven", 827, 12152),
            ("Boston Clapham Junction", 1047, 11323),
            ("Boston Waterloo", 769, 10852),
            ("Central City Beltway Terminal North", -923, -678),
            ("Sealane New Forest Station", -821, 81),
            ("Central City", 202, -820),
            ("Bakersville Penn Station", -386, -4870),
            ("Woodsdale", 159, -5514),
            ("Mihama", 265, -6249),
            ("Heights City", 1264, -6568),
            ("Quiris", 1264, -6987),
        ):
            RailStation.new(
                self,
                codes={station},
                company=company,
                world="New",
                coordinates=(x, z),
            )

        # names = []
        # for warp in warps(uuid.UUID("8ebc5173-3df2-450c-92a3-e13063409a24"), config):
        #     if not warp["name"].startswith("FR"):
        #         continue
        #     if (
        #         match := re.search(
        #             r"(?i)(?:This is|The next (?:and last )?stop is) (?!a|the)([^.]*)\.", warp["welcomeMessage"]
        #         )
        #     ) is None:
        #         # rich.print(ERROR+"Unknown warp message format:", warp['welcomeMessage'])
        #         continue
        #     name = match.group(1)
        #     name = {
        #         "Segville International": "Segville International Airport",
        #         "Zaquar Onika T": "Zaquar Onika T. Maraj Station",
        #         "UCWTIA West Station": "UCWTIA",
        #         "Boston Clapham Station": "Boston Clapham Junction",
        #         "Sealane": "Sealane New Forest Station",
        #         "Bakersville": "Bakersville Grand Central",
        #     }.get(name, name)
        #     print(name)
        #     if name in names:
        #         continue
        #     RailStation.new(self,
        #         codes={name},
        #         company=company,
        #         world="New",
        #         coordinates=(warp["x"], warp["z"]),
        #     )
        #     names.append(name)
        self.save_to_cache(config, self.g)
