import itertools
import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailSource,
    RailStation,
)


class IntraRailMCRWarp(RailSource):
    name = "MRT Warp API (Rail, IntraRail MCR)"
    priority = 0

    def build(self, config: Config):
        company = RailCompany.new(self, name="IntraRail")

        html = get_wiki_html("", config, old_id=203396)

        code2name = {}
        for table in html.find_all("table"):
            if "Code" not in table("th")[1].string:
                continue
            span = table.previous_sibling.previous_sibling.find("span", class_="mw-headline")
            if (result := re.search(r"\((?P<code>.*?)\)", span.string)) is None:
                continue
            line_code = result.group("code")
            if line_code.startswith("WM") or line_code == "db":
                continue

            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:
                    continue
                code = tr("td")[1].span.span.string
                name = "".join(tr("td")[2].strings).strip()
                code2name[code] = name.replace(" -  ", " ").replace(" - ", " ")

        names = []
        for warp in itertools.chain(
            warps(uuid.UUID("16990807-9df4-4bde-89b7-efee9836b7a6"), config),
            warps(uuid.UUID("928761c5-d95f-4e16-8761-624dada75dc2"), config),
            warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), config),
            warps(uuid.UUID("5cc70692-7282-4fd5-8d89-11c08535bb11"), config),
        ):
            if not warp["name"].startswith("MCR") or len(warp["name"].split("_")) < 2:
                continue
            code = warp["name"].split("_")[1]
            code = {
                "STAD": "STA",
                "NROC": "NRH",
                "OROC": "ROC",
            }.get(code, code)
            name = code2name["OCJS-" + warp["name"].split("_")[2]] if code == "OCJS" else code2name.get(code)
            if name is None:
                continue
            name = {
                "Gemstride-MoComm": "Gemstride",
                "Euphorial": "Deadbush Euphorial",
                "Quarryville": "Deadbush Quarryville",
                "Eep Underground": "Eep",
                "Eep Overground": "Eep",
                "Orange City": "Orange City Proper",
                "Scarborough (HQ)": "Scarborough MCR HQ",
                "New Beginnings": "New Beginnings Bus Terminal",
                "Matheson": "Matheson Lombardo Avenue",
                "Delta City": "Delta City First Street",
                "Royal Ferry": "Royal Ferry Downtown",
                "New Stone City V44": "New Stone City V43",
                "New Stone City": "New Stone City Intermodal Hub",
                "Formsa Northern": "Formosa Northern",
                "Weezerville": "Deadbush Weezerville",
                "Hacienda Mojito": "Deadbush Hacienda Mojito",
                "Volkov Bay": "Deadbush Volkov Bay",
                "Cactus River": "Cactus River SE8",
                "Zerez": "Zerez Thespe Railway Station",
                "ShadyGrove": "Shady Grove",
                "St. Roux": "Saint Roux Gare Orsay",
                "Conricsto Overground": "Conricsto",
                "Palestropol": "Palestropol North",
                "Schillerton Maple St.": "Schillerton Maple Street",
                "Boston Waterloo": "Boston Waterloo Station",
                "San Dzobiak": "San Dzobiak Union Square",
                "Siletz Salvador": "Siletz Salvador Station",
            }.get(name, name)
            if name in names:
                continue
            RailStation.new(
                self, codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"])
            )
            names.append(name)
