import re

import bs4

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_html, get_wiki_text


class WZR(RailSource):
    name = "MRT Wiki (Rail, West Zeta Rail)"
    html: bs4.BeautifulSoup

    def prepare(self, config: Config):
        self.html = get_wiki_html("List of West Zeta Rail lines", config)

    def build(self, config: Config):
        company = self.company(name="West Zeta Rail")

        for table in self.html.find_all("table"):
            if "Code" not in table.th.string:
                continue
            span = table.previous_sibling.previous_sibling.find(
                "span", class_="mw-headline"
            ) or table.previous_sibling.previous_sibling.previous_sibling.previous_sibling.find(
                "span", class_="mw-headline"
            )
            if (result := re.search(r"Line (?P<code>.*?) - (?P<name>.*)|(?P<name2>[^(]*)", span.string)) is None:
                continue
            line_name = result.group("name") or result.group("name2")
            line_code = result.group("code") or line_name
            line = self.line(code=line_code, name=line_name, company=company, mode="warp", colour="#aa0000")

            builder = self.builder(line)
            for tr in table.find_all("tr"):
                if len(tr("td")) != 4:
                    continue
                if tr("td")[3].string.strip() == "Planned":
                    continue
                code = tr("td")[0].string
                name = "".join(tr("td")[1].strings).strip().rstrip("*")
                builder.add(self.station(codes={code}, name=name, company=company))

            builder.connect()

        for line_code, line_name in (
            ("2", "Northmist Line"),
            ("10", "Centrale Line"),
        ):
            wiki = get_wiki_text(line_name, config)
            line = self.line(code=line_code, name=line_name, company=company, mode="warp", colour="#aa0000")

            builder = self.builder(line)
            for result in re.finditer(
                re.compile(
                    r"(?:\[\[(?:[^|]*\|)?(?P<name1>[^|]*)]]|{{stl\|WZR\|(?P<name2>[^|]*)}}) *\|\| *(?P<code>\w\w\w)"
                ),
                wiki,
            ):
                code = result.group("code").upper()
                name = (result.group("name1") or result.group("name2")).strip()
                builder.add(self.station(codes={code}, name=name, company=company))

            builder.connect()

        for line_code, line_name in (
            ("3", "Aurora Line"),
            ("4", "Genso Line"),
            ("8", "Ismael Line"),
        ):
            wiki = get_wiki_text(line_name, config)
            line = self.line(code=line_code, name=line_name, company=company, mode="warp", colour="#aa0000")

            builder = self.builder(line)
            for result in re.finditer(
                re.compile(r"\[\[(?:[^|]*\|)?(?P<name>[^|]*)]] *\|\| *(?P<code>\w\w\w) .*\|\|.*\|\|(?! *Planned)"), wiki
            ):
                code = result.group("code").upper()
                name = result.group("name").strip()
                builder.add(self.station(codes={code}, name=name, company=company))

            builder.connect()
