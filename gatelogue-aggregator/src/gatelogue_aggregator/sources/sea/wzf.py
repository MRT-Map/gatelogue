import re

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop


class WZF(SeaSource):
    name = "MRT Wiki (Sea, West Zeta Ferry)"
    priority = 1

    def build(self, config: Config):
        company = SeaCompany.new(self, name="West Zeta Ferry")

        html = get_wiki_html("West Zeta Ferry", config)

        for table in html.find_all("table"):
            if "Status" not in table.th.string:
                continue
            span = table.previous_sibling.previous_sibling.find(
                "span", class_="mw-headline"
            ) or table.previous_sibling.previous_sibling.previous_sibling.previous_sibling.find(
                "span", class_="mw-headline"
            )
            if (result := re.search(r"Line (?P<code>.*?) \((?P<name>.*)\)", span.string)) is None:
                continue
            line_name = result.group("name")
            line_code = result.group("code")
            line = SeaLine.new(self, code=line_code, name=line_name, company=company)

            stops = []
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:  # noqa: PLR2004
                    continue
                code = tr("td")[1].string
                name = "".join(tr("td")[2].strings)
                if "planned" in name:
                    continue
                stop = SeaStop.new(self, codes={code}, name=name, company=company)
                stops.append(stop)

                colour = tr("td")[1].attrs["style"].split(":")[1]
                line.colour = self.source(colour)

            SeaLineBuilder(self, line).connect(*stops)
