import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource


class FredRail(RailSource):
    name = "Hardcode (Rail, Fred Rail)"
    priority = 0

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="Fred Rail")

        line_name = "Main Line"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
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
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Central Line"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Bakersville Grand Central",
            "UCWTIA",
            "Segville International Airport",
            "Utopia",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Southern Regional Railroad"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Tranquil Forest Central",
            "Wythern",
            # "Astoria",
            # "Fort Yaxier West",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Richville Shuttle"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = ["Tranquil Forest Central", "Richville"]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Fort Yaxier Shuttle"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = ["Utopia", "Utopia AFK"]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Southern Central"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Utopia",
            "Whiteley Turing Square",
            # "Paddington Station",
            # "Zaquar Onika T. Maraj Station",
            # "Fort Yaxier West",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Western Line"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Utopia",
            "Kolpino",
            "Espil",
            "Kings Cross Railway Terminal",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Lodminechead Limited"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = ["Utopia", "Matheson", "Far Matheson", "San Dzobiak", "Siletz", "Dabecco", "Lodminechead"]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "New Jerseyan"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
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
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
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
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = ["New Mackinaw Union Station", "Oparia Airport"]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Grand Central Limited"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Bakersville Grand Central",
            "Central City Beltway Terminal North",
            "Sealane New Forest Station",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        # line_name = "Borehole Line"
        # line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        # stations = [
        #     "Topside",
        #     "Rival Station",
        #     "Down Under Village",
        #     "Borehole Town",
        #     "Lushful Caverns",
        # ]
        # stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        # RailLineBuilder(self, line).connect(*stations)

        line_name = "Tung Wan Shuttle"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Tung Wan Transfer",
            "Tung Wan Halt",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Central City Shuttle"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Bakersville Grand Central",
            "Central City",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Crescent Service"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = ["Bakersville Grand Central", "Woodsdale", "Mihama", "Heights City", "Quiris"]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        self.save_to_cache(config, self.g)
