from gatelogue_aggregator.types.base import Source
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import RailContext, RailLineBuilder, RailSource


class NSC(RailSource):
    name = "Hardcode (Rail, Network South Central)"
    priority = 0

    def __init__(self, config: Config):
        RailContext.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = self.rail_company(name="Network South Central")

        line_name = "InterCity 1"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Kolpino",
            "Utopia",
            "Matheson - Old Street",
            "Siletz",
            "Royal Ferry Victoria",
            "Oakley - Exchange",
            "Segville - International",
            "Musique East",
            "Musique West",
            "Aprix",
            "Glenbrook",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "InterCity 2"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Royal Ferry Paddington",
            "Subryanville",
            "Royal Ferry - Broad Street",
            "Siletz",
            "San Renoldi",
            "Thunderbird",
            "Freedon West",
            "Freedon Exchange",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)
        stations = [
            "Royal Ferry Victoria",
            "Siletz",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "InterCity 2N"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Freedon Exchange",
            "Freedon Central",
            "Freedon City Center",
            "Freedon Market",
            "Freedon Airfield",
            "Freedon International",
            "Northberg Central",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "InterCity 2S"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Freedon Exchange",
            "Freedon Edo",
            "Izumo Old Town",
            "Izumo South",
            "Izumo Mall",
            "Izumo Backlands",
            "St.Roux",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "InterCity 3"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Siletz",
            "Loundon",
            "Dabecco Main",
            "Dabecco Exchange",
            "Woodsbane",
            "Lochminehead - Trijunction",
            "Rochshire South",
            "Rochshire Central",
            "Rochshire North",
            "Grayzen Airport",
            "Grayzen Central",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "InterCity 4"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Royal Ferry Victoria",
            "Siletz",
            "Royalston",
            "Scarborough North",
            "Scarborough Central",
            "Stratos",
            "Rockham - Eamington West",
            "Rockham Central",
            "Haibian North",
            "Haibian Hall",
            "Haibian Central",
            "Sydney",
            "Astoria",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Commuter 1"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Central City",
            "Government Circle",
            "Mountainside",
            "City Hall",
            "Royal Ferry Victoria",
            "Dabecco East",
            "Siletz",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Commuter 2"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Central City",
            "Greenplain Heights",
            "Bourbon Street",
            "Kensington",
            "Oakley - Exchange",
            "Dabecco West",
            "Siletz",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Commuter 3"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Siletz",
            "San Dzobiak Union",
            "Siletz Salvador Station",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Commuter 3"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Paddington",
            "East La Penitience",
            "Subryanville",
            "Boardwalk",
            "Royal Ferry Broad St",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Commuter 5"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Royal Ferry Victoria",
            "Kensington",
            "UCWTIA",
            "Little Italy",
            "Formosa Harbor",
            "Mount Exclave",
            "League of Cities",
            "Danielston Paisley Place",
            "Danielston South",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "High Speed 1"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Central City",
            "Royal Ferry - Broad Street",
            "Siletz",
            "Matheson Junction",
            "Utopia",
            "Kolpino",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "High Speed 2"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Central City",
            "Royal Ferry - Broad Street",
            "Segville",
            "Evella",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).connect(*stations)

        line_name = "Central Cities Rail Loop"
        line = self.rail_line(code=line_name, name=line_name, company=company, mode="warp")
        stations = [
            "Royal Ferry Victoria",
            "Dabecco Exchange",
            "Sylvania",
            "Lochminehead -Trijunction",
            "MRT Land",
            "Rochshire Central",
            "Grayzen Transit Hub",
            "Central City",
            "Spruce Neck North",
            "Ashmore",
            "Mons Pratus",
            "Xilia",
            "42",
            "Formosa Northern",
            "Formosa City Hall",
            "UCWTIA",
            "Greenmount",
            "PieVille",
            "Kensington",
        ]
        stations = [self.rail_station(codes={s}, name=s, company=company) for s in stations]
        RailLineBuilder(self, line).circle(*stations)

        self.save_to_cache(config, self.g)
