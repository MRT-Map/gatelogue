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


class NSC(RailSource):
    name = "MRT Wiki (Rail, Network South Central)"
    priority = 0

    def build(self, config: Config):
        company = RailCompany.new(self, name="Network South Central")

        html = get_wiki_html("Network South Central", config)
        line_table = html.find_all("table")[2]

        line_prefix = ""
        for tr in line_table.p.find_all("tr")[1:]:
            if len(tr("th")) == 1 and tr.th.b is not None:
                if tr.th.b.string != "Special Services":
                    line_prefix = tr.th.b.string.strip() + " "
                continue

            if "Line Under Construction" in str(tr("th")[5]):
                continue
            line_name = line_prefix + str(tr("th")[0])
            line = RailLine.new(self, code=line_name, name=line_name, company=company, mode="warp")

            stations = [str(tr("th")[1])] + [str(a).removesuffix("*") for a in tr("th")[3].strings]
            if tr("th")[2] != "No end":
                stations += [str(tr("th")[2])]
            for station in stations:
                RailStation.new(self, codes={station}, name=station, company=company)

            if len(stations) == 0:
                continue

            if line_name == "Commuter 4":
                RailLineBuilder(self, line).connect(*stations[-5:])
            elif line_name == "Central Cities Rail Loop":
                RailLineBuilder(self, line).circle(*stations)
            else:
                RailLineBuilder(self, line).connect(*stations)

            rich.print(RESULT + f"NSC {line_name} has {len(stations)} stations")
