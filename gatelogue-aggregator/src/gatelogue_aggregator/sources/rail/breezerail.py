from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)


class BreezeRail(RailSource):
    name = "MRT Wiki (Rail, BreezeRail)"
    priority = 1

    def build(self, config: Config):
        company = RailCompany.new(self, name="BreezeRail")

        html = get_wiki_html("BreezeRail", config)

        for h3 in html.find_all("h3"):
            if (line_code_name := h3.find("span", class_="mw-headline")) is None:
                continue
            line_code, line_name = line_code_name.string.split(" - ", 1)
            line = RailLine.new(self, code=line_code, name=line_name, company=company, colour="#00c3ff")

            stations = []
            for tr in h3.next_sibling.next_sibling.find_all("tr")[1:]:
                if tr("td")[0].find("a", href="/index.php/File:Dynmap_Green_Flag.png") is None:
                    continue
                name = next(tr("td")[2].strings)
                code = tr("td")[1].span.string
                code = {"SP", "SPC"} if code == "SP" else {code}

                station = RailStation.new(self, codes=code, name=name, company=company)
                stations.append(station)

            RailLineBuilder(self, line).connect(*stations)
