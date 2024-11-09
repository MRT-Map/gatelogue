import re

import rich

from gatelogue_aggregator.logging import RESULT
from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.node.sea import SeaCompany, SeaLine, SeaLineBuilder, SeaSource, SeaStop
from gatelogue_aggregator.types.source import Source


class WZF(SeaSource):
    name = "MRT Wiki (Sea, West Zeta Ferry)"
    priority = 0

    def __init__(self, config: Config):
        SeaSource.__init__(self)
        Source.__init__(self, config)
        if (g := self.retrieve_from_cache(config)) is not None:
            self.g = g
            return

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
            line = SeaLine.new(self, code=str(line_code).strip(), name=str(line_name).strip(), company=company)

            stops = []
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:  # noqa: PLR2004
                    continue
                code = str(tr("td")[1].span.string).strip()
                name = "".join(tr("td")[2].strings).strip()
                if "planned" in name:
                    continue
                stop = SeaStop.new(self, codes={code}, name=name, company=company)
                stops.append(stop)

                colour = tr("td")[1].attrs["style"].split(":")[1]
                line.colour = self.source(colour)

            SeaLineBuilder(self, line).connect(*stops)

            rich.print(RESULT + f"WZF Line {line_code} has {len(stops)} stations")
        self.save_to_cache(config, self.g)
