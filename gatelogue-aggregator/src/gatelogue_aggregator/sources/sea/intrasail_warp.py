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
                "the Port of Ilirea": "Port of Ilirea",
                "Ilirea Port of Ilirea": "Port of Ilirea",
                "Xandar-Vekta Ferry Terminal": "Xandar-Vekta Transfer Station",
                "Weezerville": "Deadbush Port of Weezerville",
                "New Southport Port of New Southport": "Port of New Southport",
                "New Singapore Port of New Singapore": "Port of New Singapore",
                "Deadbush Port of Deadbush": "Port of Deadbush",
                "Whitechapel South Whitechapel Ferry Terminal": "South Whitechapel Ferry Terminal",
                "Alexandriasburg Island of Alexandriasburg Port of Call": "Alexandriasburg Island of Alexandria Port of Call",
            }.get(name, name)
            if "%warp%" in name:
                continue
            if name in names:
                continue

            SeaStop.new(self, codes={name}, company=company, name=name, world="New", coordinates=(warp["x"], warp["z"]))
            names.append(name)
