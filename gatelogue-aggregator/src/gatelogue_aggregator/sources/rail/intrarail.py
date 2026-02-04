import bs4

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.utils import get_stn


class IntraRail(RailSource):
    name = "MRT Wiki (Rail, IntraRail)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("IntraRail", config)


    def build(self, config: Config):
        company = self.company(name="IntraRail")

        for h4 in self.html.find_all("h4"):
            line_code_name: str = h4.find("span", class_="mw-headline").string
            if line_code_name.startswith("("):
                continue
            line_code = line_code_name.split(" ")[0]
            line_name = line_code_name.removeprefix(line_code)

            line_code_base = int(line_code.removesuffix("X").removesuffix("A").removesuffix("W").removesuffix("E"))
            line_colour = (
                "#f083a6"
                if line_code.endswith("X") and 0 <= line_code_base <= 199
                else "#63dcd6"
                if 0 <= line_code_base <= 199
                else "#db100c"
                if 200 <= line_code_base <= 299
                else "#22da4f"
                if 300 <= line_code_base <= 399
                else "#f4be1b"
                if 400 <= line_code_base <= 499
                else "#0000ff"
                if 500 <= line_code_base <= 599
                else "#888"
            )

            line = self.line(company=company, code=line_code, name=line_name, mode="warp", colour=line_colour)

            builder = self.builder(line)
            for big in h4.find_next("p").find_all("big", recursive=False):
                if (big2 := big.find("big")) is None or big.find("s") is not None:
                    continue
                name = " ".join(big2.stripped_strings)
                name = {"Plage Rouge Seki City": "Plage Rouge-Seki City"}.get(name, name)

                builder.add(self.station(company=company, codes={name}, name=name))

            if line_code == "2X":
                builder2 = builder.copy()
                builder2.connect_to("Formosa Northern", forward_direction=f"towards {builder2.station_list[-1].name}")
                builder2.connect_to("UCWT International Airport East", forward_direction=f"towards {builder2.station_list[-1].name}")

                builder3 = builder.copy()
                builder3.connect_to("Central City Warp Rail Terminal", forward_direction=f"towards {builder3.station_list[-1].name}")
                builder3.connect_to("Achowalogen Takachsin-Covina International Airport", forward_direction=f"towards {builder3.station_list[-1].name}")
                builder3.connect_to("Siletz Salvador Station", forward_direction=f"towards {builder3.station_list[-1].name}")

            if line_code == "202":
                builder.connect(until_before="Amestris Cummins Highway")
                builder.branch_detached(join_back_at="Laclede Airport Plaza").connect(until="Laclede Airport Plaza", backward_direction="towards Amestris Cummins Highway")
                builder.connect()
            else:
                builder.connect()
