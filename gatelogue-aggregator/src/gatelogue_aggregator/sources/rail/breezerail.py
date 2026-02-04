import bs4

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html


class BreezeRail(RailSource):
    name = "MRT Wiki (Rail, BreezeRail)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("BreezeRail", config)

    def build(self, config: Config):
        company = self.company(name="BreezeRail")

        for h3 in self.html.find_all("h3"):
            if (line_code_name := h3.find("span", class_="mw-headline")) is None:
                continue
            line_code, line_name = line_code_name.string.split(" - ", 1)
            line = self.line(code=line_code, name=line_name, company=company, colour="#00c3ff")

            builder = self.builder(line)
            for tr in h3.next_sibling.next_sibling.find_all("tr")[1:]:
                if tr("td")[0].find("a", href="/index.php/File:Dynmap_Green_Flag.png") is None:
                    continue
                name = next(tr("td")[2].strings)
                code = tr("td")[1].span.string
                code = {"SP", "SPC"} if code == "SP" else {code}

                builder.add(self.station(codes=code, name=name, company=company))

            builder.connect()
