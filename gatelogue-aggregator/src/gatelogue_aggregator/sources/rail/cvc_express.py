from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.rail import (
    RailCompany,
    RailLine,
    RailLineBuilder,
    RailSource,
    RailStation,
)


class CVCExpress(RailSource):
    name = "MRT Wiki (Rail, CVCExpress)"
    priority = 1

    def build(self, config: Config):
        company = RailCompany.new(self, name="CVCExpress")

        html = get_wiki_html("CVCExpress", config)
        for h3 in html.find_all("h3"):
            line_code_name = h3.find("span", class_="mw-headline").string
            line_code, line_name = line_code_name.split(" -- ")
            line = RailLine.new(self, code=line_code, name=line_name, company=company, mode="traincarts", colour="#c00")

            ul = h3.next_sibling.next_sibling
            stations = []
            for li in ul.find_all("li"):
                name = li.string.strip()
                station = RailStation.new(self, codes={name}, name=name, company=company)
                stations.append(station)

            if len(stations) == 0:
                continue

            RailLineBuilder(self, line).connect(*stations)

