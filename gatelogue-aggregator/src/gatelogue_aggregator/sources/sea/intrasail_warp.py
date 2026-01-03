import re
import uuid

from gatelogue_aggregator.downloader import warps
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaSource, SeaStop


class IntraSailWarp(SeaSource):
    name = "MRT Warp API (Sea, IntraSail)"
    priority = 0

    def build(self, config: Config):
        company = SeaCompany.new(self, name="IntraSail")

        names = []
        for warp in warps(uuid.UUID("0a0cbbfd-40bb-41ea-956d-38b8feeaaf92"), config):
            if not warp["name"].startswith("IS"):
                continue
            if warp["name"] == "IS1d-KZH-WB":
                name = "Kazeshima Kuzuhamachi"
            else:
                if (
                    match := re.search(
                        r"(?i)^Welcome to ([^,]*),|^THIS & LAST STOP: ([^/]*) /|(?:THIS|LAST) STOP: ([^/]*) /",
                        warp["welcomeMessage"],
                    )
                ) is None:
                    # rich.print(ERROR + "hUnknown warp message format:", warp['welcomeMessage'])
                    continue

                name = match.group(1) or match.group(2) or match.group(3)
                name = {
                    "Shahai": "Shahai Ferry Terminal",
                    "Auburn": "Auburn Marina",
                    "the Port of Ilirea": "Ilirea Port of Ilirea",
                    "Xandar-Vekta Ferry Terminal": "Xandar-Vekta Transfer Station",
                    "Weezerville": "Deadbush Port of Weezerville",
                    "Alexandriasburg Island of Alexandriasburg Port of Call": "Alexandriasburg Island of Alexandria Port of Call",
                    "Port Diamondback": "Port Diamondback Port",
                    "Fort Yaxier": "Fort Yaxier Canalside",
                    "Puerto de El Caserío": "El Caserío Puerto de El Caserío",
                    "Port Elizabeth Victoria": "Victoria Port Elizabeth Victoria",
                    "Port Sonder": "Port Sonder Passenger Port",
                    "Bakersville Bay": "Bakersville South Ferry Terminal",
                }.get(name, name)
                if "%warp%" in name or name == "Stoneedge":
                    continue
            if name in names:
                continue

            SeaStop.new(self, codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
