from __future__ import annotations

import msgspec
import rich

from gatelogue_aggregator.logging import ERROR
from gatelogue_aggregator.types.source import Source


class SharedFacility(msgspec.Struct):
    pass


class SharedFacilitySource(Source):
    name = "Gatelogue"
    priority = 0

    def update(self):
        from gatelogue_aggregator.types.node.rail import RailCompany, RailStation

        blu = "BluRail"
        fr = "Fred Rail"
        intra = "IntraRail"
        mrt = "MRT"
        mtc = "MarbleRail"
        nflr = "nFLR"
        redtrain = "RedTrain"
        rn = "RailNorth"
        rlq = "RaiLinQ"
        wzr = "West Zeta Rail"
        seat = "SEAT"
        pac = "Pacifica"
        flrk = "FLR Kazeshima/Shui Chau"
        flrf = "FLR Foresne/Commuter"

        for company1, station1_name, company2, station2_name in (
            (nflr, "Dand Grand Central", intra, "Dand Grand Central"),
            (blu, "Dand Central", intra, "Dand Grand Central"),
            (intra, "Foresne Liveray", nflr, "Foresne Liveray"),
            (intra, "Tembok Railway Station", nflr, "Tembok"),
            (wzr, "Tembok", nflr, "Tembok"),
            (nflr, "Tembok", mrt, "Tembok"),
            (blu, "Heampstead Kings Cross", intra, "Deadbush Heampstead Kings Cross Railway Terminal"),
            (fr, "Kings Cross Railway Terminal", intra, "Deadbush Heampstead Kings Cross Railway Terminal"),
            (blu, "Schillerton Maple Street", intra, "Schillerton Maple Street"),
            (blu, "Boston Waterloo", intra, "Boston Waterloo Station"),
            (mtc, "Boston Waterloo", intra, "Boston Waterloo Station"),
            (fr, "Boston Waterloo", intra, "Boston Waterloo Station"),
            (mtc, "Boston Clapham Junction", fr, "Boston Clapham Junction"),
            (intra, "Boston Clapham Junction", fr, "Boston Clapham Junction"),
            (blu, "Zaquar Tanzanite Station", intra, "Zaquar Tanzanite Station"),
            (blu, "San Dzobiak Union Station", intra, "San Dzobiak Union Square"),
            (redtrain, "San Dzobiak Union Square", intra, "San Dzobiak Union Square"),
            (fr, "San Dzobiak", intra, "San Dzobiak Union Square"),
            (blu, "Siletz Salvador Station", intra, "Siletz Salvador Station"),
            (fr, "Siletz", intra, "Siletz Salvador Station"),
            (redtrain, "Siletz Salvador Station", intra, "Siletz Salvador Station"),
            (fr, "Lochminehead", intra, "Lochminehead Trijunction"),
            (blu, "Los Angeles-Farwater Union Station", intra, "Los Angeles-Farwater Union Station"),
            (blu, "Valemount", intra, "Valemount"),
            (blu, "Ravenna Union Station", intra, "Ravenna Union Station"),
            (blu, "New Gensokyo Hakurei Shrine", intra, "New Gensokyo Hakurei Shrine"),
            (blu, "New Gensokyo Regional Airport", intra, "New Gensokyo Regional Airport"),
            (blu, "Shark Town", intra, "Shark Town"),
            (blu, "Bechtel", intra, "Bechtel"),
            (blu, "Niwen", intra, "Niwen Train Station"),
            (blu, "Risima", intra, "Risima"),
            (blu, "Rank Resort Central", intra, "Rank Resort Central"),
            (blu, "Whitecliff Central", intra, "Whitecliff Central"),
            (rlq, "Whitecliff Central", intra, "Whitecliff Central"),
            (blu, "Segav Sal", intra, "Segav Sal"),
            (blu, "Northlend", intra, "Northlend Union Station"),
            (rlq, "Northlend Union", intra, "Northlend Union Station"),
            (rlq, "Vegeta Junction", intra, "Vegeta Junction"),
            (blu, "Broxbourne", intra, "Broxbourne"),
            (blu, "Ilirea Transit Center", intra, "Ilirea Transit Center"),
            (rlq, "Ilirea ITC", intra, "Ilirea Transit Center"),
            (intra, "Ilirea Airport Station", blu, "Ilirea Midcity Airport"),
            (rlq, "Ilirea Airport", blu, "Ilirea Midcity Airport"),
            (blu, "Waverly", intra, "Waverly Edinburgh Station"),
            (
                blu,
                "UCWT International Airport West",
                intra,
                "UCWT International Airport West",
            ),
            (fr, "UCWTIA", intra, "UCWT International Airport West"),
            (blu, "Sealane Central", intra, "Sealane Central"),
            (rlq, "Sealane Central", intra, "Sealane Central"),
            (blu, "Central City Warp Rail Terminal", intra, "Central City Warp Rail Terminal"),
            (rlq, "Central City", intra, "Central City Warp Rail Terminal"),
            (fr, "Central City", intra, "Central City Warp Rail Terminal"),
            (redtrain, "Central City Warp Rail Terminal", intra, "Central City Warp Rail Terminal"),
            (fr, "Sealane New Forest Station", intra, "Sealane New Forest Terminal"),
            (fr, "Central City Beltway Terminal North", intra, "Central City Beltway Terminal North"),
            (blu, "Utopia - AFK", intra, "Utopia Anthony Fokker Transit Hub"),
            (fr, "Utopia AFK", intra, "Utopia Anthony Fokker Transit Hub"),
            (blu, "Venceslo", intra, "Venceslo Union Station"),
            (redtrain, "Venceslo", intra, "Venceslo Union Station"),
            (blu, "Laclede Central", intra, "Laclede Central"),
            (rlq, "Laclede Central", intra, "Laclede Central"),
            (blu, "Vermilion", intra, "Vermilion Victory Square"),
            (blu, "Bakersville Grand Central", intra, "Bakersville Grand Central"),
            (fr, "Bakersville Grand Central", intra, "Bakersville Grand Central"),
            (fr, "Westchester Junction", intra, "Bakersville Westchester Junction - Canal Works"),
            (blu, "Whitechapel Border", intra, "Whitechapel Border"),
            (blu, "Waterville Union Station", intra, "Waterville Union Station"),
            (blu, "Fort Yaxier Central", intra, "Fort Yaxier Central"),
            (blu, "Sunshine Coast Máspalmas Terminal", intra, "Sunshine Coast Máspalmas Terminal"),
            (blu, "Murrville Central", intra, "Murrville Central"),
            (blu, "BirchView Central", intra, "BirchView Central"),
            (rlq, "Birchview Central", intra, "BirchView Central"),
            (rlq, "Titsensaki", blu, "Titsensaki North City"),
            (rlq, "East Mesa", intra, "East Mesa M. Bubbles Station"),
            (rlq, "Mons Pratus", intra, "Mons Pratus Transportation Hub"),
            (rlq, "Segville International", intra, "Segville International Airport"),
            (blu, "Segville International", intra, "Segville International Airport"),
            (fr, "Segville International Airport", intra, "Segville International Airport"),
            (rlq, "Utopia Central", blu, "Utopia Central"),
            (rlq, "Utopia Stephenson", blu, "Utopia Stephenson"),
            (rlq, "Utopia IKEA", blu, "Utopia - IKEA"),
            (blu, "Saint Roux", intra, "Saint Roux Gare Orsay"),
            (rlq, "Saint Roux Gare Orsay", intra, "Saint Roux Gare Orsay"),
            (nflr, "Port of Porton", mrt, "Porton"),
            (nflr, "Uacam Beach", mrt, "Uacam Beach East"),
            (nflr, "M90 Theme Park", mrt, ["M90"]),
            (nflr, "Castlehill", mrt, ["U126"]),
            (nflr, "Lilygrove Union", mrt, "Lilygrove Union Station/Heliport"),
            (nflr, "Dewford City Lometa", wzr, "Dewford City Lometa Station"),
            (mtc, "Cape Cambridge John Glenn", nflr, "Cape Cambridge John Glenn Transit Centre"),
            (mtc, "Port Sonder", nflr, "Port Sonder"),
            (mtc, "Sandfield", nflr, "Sandfield"),
            (mtc, "Seolho Midwest", nflr, "Seolho Midwest"),
            (mtc, "Oceanside Bayfront", nflr, "Oceanside Bayfront"),
            (mtc, "Tung Wan", nflr, "Tung Wan"),
            (mtc, "Edwardsburg", nflr, "Edwardsburg"),
            (blu, "Musique", mrt, "Musique"),
            (blu, "Elecna Bay North", intra, "Elecna Bay North"),
            (rlq, "Elecna Bay North", intra, "Elecna Bay North"),
            (rlq, "Outer Solarion", intra, "Achowalogen Takachsin Outer Solarion"),
            (rlq, "Downtown Solarion", intra, "Achowalogen Takachsin Downtown Solarion"),
            (rlq, "Achowalogen Takachsin Suburb", intra, "Achowalogen Takachsin Suburb"),
            (rlq, "Downtown Achowalogen Takachsin/Covina", intra, "Achowalogen Takachsin-Covina Downtown"),
            (rlq, "Achowalogen Takachsin Western Transportation Hub", intra, "Achowalogen Takachsin West"),
            (blu, "Achowalogen Takachsin West", intra, "Achowalogen Takachsin West"),
            (
                blu,
                "Achowalogen Takachsin-Covina International Airport",
                intra,
                "Achowalogen Takachsin-Covina International Airport",
            ),
            (rlq, "ATC International Airport", intra, "Achowalogen Takachsin-Covina International Airport"),
            (blu, "Chalxior Femtoprism Airfield", intra, "Chalxior Femtoprism Airfield"),
            (rn, "Chalxior", intra, "Chalxior Femtoprism Airfield"),
            (blu, "Pilmont", intra, "Pilmont"),
            (rn, "Pilmont", intra, "Pilmont"),
            (rn, "New Acreadium", intra, "New Acreadium Central District"),
            (blu, "Schiphol International Airport", intra, "New Acreadium Schiphol Airport"),
            (rn, "New Acreadium Schiphol Int'l", intra, "New Acreadium Schiphol Airport"),
            (blu, "Antioch Union Station", intra, "Antioch Union Station"),
            (rlq, "Antioch", intra, "Antioch Union Station"),
            (rn, "Antioch", intra, "Antioch Union Station"),
            (blu, "Antioch Regional Airfield", intra, "Antioch Regional Airfield"),
            (rlq, "Moramoa Wyndham Street", blu, "Moramoa Wyndham Street"),
            (rlq, "Moramoa Central", blu, "Moramoa Central"),
            (intra, "Seuland", blu, "Seuland"),
            (intra, "Whiteley Turing Square", rlq, "Whiteley Turing Square"),
            (fr, "Whiteley Turing Square", rlq, "Whiteley Turing Square"),
            (blu, "Whiteley College Park", rlq, "Whiteley College Park"),
            (rn, "Kappen", mrt, "Kappen Hauptbahnhof"),
            (intra, "Royalston", mrt, ["V14"]),
            (intra, "Tranquil Forest Central", fr, "Tranquil Forest Central"),
            (blu, "Tranquil Forest Central", fr, "Tranquil Forest Central"),
            (blu, "Sesby MRT Warptrain Museum", rlq, "Sesby MRT Warptrain Museum"),
            (blu, "Sesby Central", rlq, "Sesby Central"),
            (blu, "Airchester Central", rlq, "Airchester Central"),
            (blu, "Accerton", rlq, "Accerton"),
            (nflr, "West Mesa International Airport / Blackwater", intra, "Deadbush Blackwater / WMI"),
            (blu, "Oparia Downtown", intra, "Oparia Downtown"),
            (rlq, "Oparia Downtown", intra, "Oparia Downtown"),
            (rn, "Oparia Downtown", intra, "Oparia Downtown"),
            (mrt, "Oparia Downtown", intra, "Oparia Downtown"),
            (blu, "Oparia LeTourneau International Airport", intra, "Oparia LeTourneau International Airport"),
            (rn, "Oparia LeTourneau International Airport", intra, "Oparia LeTourneau International Airport"),
            (blu, "Woodsdale", fr, "Woodsdale"),
            (blu, "Kaloro City Sports Park", intra, "Kaloro City Sports Park"),
            (blu, "Kaloro City Central", intra, "Kaloro City Central"),
            (blu, "Dogwood Madison Beach Station", intra, "Dogwood Madison Beach Station"),
            (blu, "Sand Central", intra, "Sand Central"),
            (blu, "Laarbroek", intra, "Laarbroek"),
            (blu, "Arcadium", intra, "Arcadium"),
            (
                blu,
                "Miu Wan Tseng Tsz Leng International Airport Terminal 1",
                intra,
                "Miu Wan Tseng Tsz Leng International Airport Terminal 1",
            ),
            (
                blu,
                "Miu Wan Tseng Tsz Leng International Airport Terminal 2",
                intra,
                "Miu Wan Tseng Tsz Leng International Airport Terminal 2",
            ),
            (blu, "Miu Sai", intra, "Miu Sai"),
            (blu, "Kwai Tin", intra, "Kwai Tin"),
            (blu, "Snowtopic Outskirts", intra, "Snowtopic Outskirts"),
            (blu, "Snowtopic Industrial", intra, "Snowtopic Boulevard"),
            (blu, "Hytown Union", intra, "Hytown Union"),
            (blu, "Miu Wan Kau Heung Airport", intra, "Miu Wan Kau Heung Airport"),
            (seat, "Central City Warp Terminal", rlq, "Central City"),
            (seat, "UCWTIA", fr, "UCWTIA"),
            (seat, "Willow Transit Centre", intra, "Willow Unrealistic Transport Terminal"),
            (mrt, "Larkspur - LAR Airport", blu, "Larkspur Lilyflower International Airport"),
            (intra, "Larkspur Lilyflower International Airport", blu, "Larkspur Lilyflower International Airport"),
            (rlq, "Larkspur Lilyflower", blu, "Larkspur Lilyflower International Airport"),
            (seat, "Larkspur LRT Airport", blu, "Larkspur Lilyflower International Airport"),
            (nflr, "New Genisys", seat, "New Genisys"),
            (nflr, "Foresne Liveray", seat, "Foresne Liveray"),
            (nflr, "New Izumo", seat, "New Izumo"),
            (nflr, "Peacopolis", seat, "Peacopolis"),
            (nflr, "Seolho Midwest", seat, "Seolho Midwest"),
            (blu, "Boston Waterloo", seat, "Boston Waterloo"),
            (mrt, "Bean City", pac, "Bean City"),
            (rlq, "Janghwa City", pac, "Janghwa Northern Union"),
            (intra, "Birdhall Transit Hub", pac, "Birdhall"),
            (nflr, "Deadbush International Airport", pac, "Deadbush International Airport"),
            (mrt, "New Chandigarh West", pac, "New Chandigarh"),
            (flrk, "Dirtia Bridge", nflr, "Dirtia Bridge"),
            (flrk, "Chūōkochō", nflr, "Chūōkochō"),
            (flrk, "Sakyūchō", nflr, "Sakyūchō"),
            (flrk, "Aomi", nflr, "Aomi"),
            (flrf, "Liveray", nflr, "Foresne Liveray"),
            (flrf, "Solstinox Zoo", nflr, "Foresne Solstinox"),
            (flrf, "Cinnameadow", nflr, "New Foresne Cinnameadow"),
            (flrk, "Tsukihama", nflr, "Tsukihama"),
        ):

            def is_desired_station(a, company, station_name):
                return (
                    isinstance(a, RailStation)
                    and (
                        station_name[0] in a.codes
                        if isinstance(station_name, list)
                        else (a.name is not None and a.name.v.strip() == station_name)
                    )
                    and a.get_one(self, RailCompany).name == company
                )

            station1 = next((a for a in self.g.nodes() if is_desired_station(a, company1, station1_name)), None)
            station2 = next((a for a in self.g.nodes() if is_desired_station(a, company2, station2_name)), None)
            if station1 is None:
                rich.print(ERROR + f"{company1} {station1_name} does not exist")
                continue
            if station2 is None:
                rich.print(ERROR + f"{company2} {station2_name} does not exist")
                continue
            station1.connect(self, station2, SharedFacility())
