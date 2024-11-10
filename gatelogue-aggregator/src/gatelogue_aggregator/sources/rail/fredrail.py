from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.source import Source


class FredRail(RailSource):
    name = "Hardcode (Rail, Fred Rail)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="Fred Rail")

        line_name = "Main Line"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Bakersville Grand Central",
            "Westchester Junction",
            "New Risima",
            "Xilia",
            "Formosa",
            "UCWTIA",
            "Segville International Airport",
            "Matheson Swamps",
            "Astoria",
            "Fort Yaxier Central",
            "Fort Yaxier Penn",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Central Line"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Bakersville Grand Central",
            "UCWTIA",
            "Segville International Airport",
            "Utopia",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Southern Regional Railroad"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Tranquil Forest Central",
            "Wythern",
            # "Astoria",
            # "Fort Yaxier West",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Richville Shuttle"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = ["Tranquil Forest Central", "Richville"]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Fort Yaxier Shuttle"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = ["Utopia", "Utopia AFK"]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Southern Central"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Utopia",
            "Whiteley Turing Square",
            # "Paddington Station",
            # "Zaquar Onika T. Maraj Station",
            # "Fort Yaxier West",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Western Line"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Utopia",
            "Kolpino",
            "Espil",
            "Kings Cross Railway Terminal",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Lochminehead Limited"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = ["Utopia", "Matheson", "Far Matheson", "San Dzobiak", "Siletz", "Dabecco", "Lochminehead"]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "New Jerseyan"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Boston Waterloo",
            "Boston Clapham Junction",
            "New Haven",
            "Tung Wan Transfer",
            "Palo Alto",
            "Concord",
            "Redwood Ferry",
            "Victoria Ferry",
            "Victoria Preston",
            "Veldberg",
            "Princeton Junction",
            "Rattlerville Central",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        forward_label = "towards Boston Waterloo"
        backward_label = "towards Rattlerville Central"
        RailLineBuilder(self, line).connect(*stations[:3], forward_label=forward_label, backward_label=backward_label)
        RailLineBuilder(self, line).connect(
            *stations[2:5], forward_label=forward_label, backward_label=backward_label, one_way=True
        )
        RailLineBuilder(self, line).connect(
            stations[4], stations[2], forward_label=backward_label, backward_label=forward_label, one_way=True
        )
        RailLineBuilder(self, line).connect(*stations[4:], forward_label=forward_label, backward_label=backward_label)

        line_name = "Blue Water"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = ["New Mackinaw Union Station", "Oparia Airport"]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Grand Central Limited"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Bakersville Grand Central",
            "Central City Beltway Terminal North",
            "Sealane New Forest Station",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        # line_name = "Borehole Line"
        # line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        # stations = [
        #     "Topside",
        #     "Rival Station",
        #     "Down Under Village",
        #     "Borehole Town",
        #     "Lushful Caverns",
        # ]
        # stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        # RailLineBuilder(self, line).connect(*stations)

        line_name = "Tung Wan Shuttle"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Tung Wan Transfer",
            "Tung Wan Halt",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Central City Shuttle"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Bakersville Grand Central",
            "Central City",
        ]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Crescent Service"
        line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")
        stations = ["Bakersville Grand Central", "Woodsdale", "Mihama", "Heights City", "Quiris"]
        stations = [RailStation.new(self, codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        self.save_to_cache(config, self.g)
