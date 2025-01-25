import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)
from gatelogue_aggregator.types.source import Source


class IntraRail(RailSource):
    name = "MRT Wiki (Rail, IntraRail)"
    priority = 1

    def __init__(self, config: Config):
        RailSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

        company = RailCompany.new(self, name="IntraRail")

        html = get_wiki_html("IntraRail", config)

        for h4 in html.find_all("h4"):
            line_code_name: str = h4.find("span", class_="mw-headline").string
            if line_code_name.startswith("("):
                continue
            line_code = line_code_name.split(" ")[0]
            line_name = line_code_name.removeprefix(line_code)

            line_code_base = int(line_code.removesuffix("X").removesuffix("A"))
            line_colour = (
                "#f083a6"
                if line_code.endswith("X") and 0 <= line_code_base <= 199  # noqa: PLR2004
                else "#63dcd6"
                if 0 <= line_code_base <= 199  # noqa: PLR2004
                else "#db100c"
                if 200 <= line_code_base <= 299  # noqa: PLR2004
                else "#22da4f"
                if 300 <= line_code_base <= 399  # noqa: PLR2004
                else "#f4be1b"
                if 400 <= line_code_base <= 499  # noqa: PLR2004
                else "#0000ff"
                if 500 <= line_code_base <= 599  # noqa: PLR2004
                else "#888"
            )

            line = RailLine.new(self, company=company, code=line_code, name=line_name, mode="warp", colour=line_colour)

            stations = []
            for big in h4.find_next("p").find_all("big", recursive=False):
                if (big2 := big.find("big")) is None:
                    continue
                name = " ".join(big2.stripped_strings)

                station = RailStation.new(self, company=company, codes={name}, name=name)
                stations.append(station)

            if line_code == "202":
                RailLineBuilder(self, line).connect(*stations, exclude=["Amestris Cummins Highway"])
                RailLineBuilder(self, line).connect(
                    *stations, between=("Amestris Cummins Highway", "Laclede Airport Plaza"),
                    forward_label="to Bakersville Grand Central",
                )
            else:
                RailLineBuilder(self, line).connect(*stations)

            if line_code == "2X":
                RailLineBuilder(self, line).connect(*stations, between=("Formosa Northern", "UCWT International Airport East"), exclude=["Danielston Paisley Place Transportation Center"], forward_label="to Siletz Salvador Station", backward_label="Whitechapel Border")
                RailLineBuilder(self, line).connect(*stations, between=("Central City Warp Rail Terminal", "Siletz Salvador Station"), exclude=["Rochshire", "Woodsbane"], backward_label="Whitechapel Border")

            rich.print(RESULT + f"IntraRail Line {line_code} has {len(stations)} stations")

        self.save_to_cache(config, self.g)
