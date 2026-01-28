import re

import bs4

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import SeaSource


class WZF(SeaSource):
    name = "MRT Wiki (Sea, West Zeta Ferry)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("West Zeta Ferry", config)

    def build(self, config: Config):
        company = self.company(name="West Zeta Ferry")

        for table in self.html.find_all("table"):
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
            line = self.line(code=line_code, name=line_name, company=company)

            builder = self.builder(line)
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:
                    continue
                code = next(tr("td")[1].strings)
                name = "".join(tr("td")[2].strings)
                if "planned" in name:
                    continue
                builder.add(self.stop(codes={code}, name=name, company=company))

                colour = tr("td")[1].attrs["style"].split(":")[1]
                line.colour = colour

            if len(builder.station_list) == 0:
                continue
            builder.connect()
