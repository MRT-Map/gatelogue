import bs4

from gatelogue_aggregator.sources.wiki_base import get_wiki_html
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource


class CVCExpress(RailSource):
    name = "MRT Wiki (Rail, CVCExpress)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("CVCExpress", config)

    def build(self, config: Config):
        company = self.company(name="CVCExpress")

        for h3 in self.html.find_all("h3"):
            line_code_name = h3.find("span", class_="mw-headline").string
            line_code, line_name = line_code_name.split(" -- ")
            line = self.line(code=line_code, name=line_name, company=company, mode="traincarts", colour="#c00")

            ul = h3.find_next("ul")
            builder = self.builder(line)
            for li in ul.find_all("li"):
                name = li.string.strip()
                builder.add(self.station(codes={name}, name=name, company=company))

            
            builder.connect()
