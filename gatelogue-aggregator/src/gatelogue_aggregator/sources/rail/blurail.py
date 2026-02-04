import json
import re

from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.source import RailSource
from gatelogue_aggregator.sources.wiki_base import get_wiki_text
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.utils import search_all


class BluRail(RailSource):
    name = "MRT Wiki (Rail, BluRail)"
    line_wikis: dict[str, str] = {}

    def prepare(self, config: Config):
        line_list = json.loads(
            get_url(
                "https://wiki.minecartrapidtransit.net/api.php?action=query&list=categorymembers&cmtitle=Category%3ABluRail+lines&cmlimit=5000&format=json",
                config.cache_dir / "blurail_line_list",
                config.timeout,
                cooldown=config.cooldown,
                )
        )["query"]["categorymembers"]

        line_codes = [result["title"].removesuffix(" (BluRail line)") for result in line_list]

        for line_code in line_codes:
            wiki = get_wiki_text(f"{line_code} (BluRail line)", config)
            if "is a planned [[BluRail]] warp train line" in wiki:
                continue
            self.line_wikis[line_code] = wiki

    def build(self, config: Config):
        company = self.company(name="BluRail")

        for line_code, wiki in self.line_wikis.items():
            line_name = re.search(r"\| linelong = (.*)\n", wiki).group(1)

            line_colour = (
                "#c01c22"
                if line_code.endswith("X") and line_code[0].isdigit()
                else "#0a7ec3"
                if line_code[-1].isdigit()
                else "#0c4a9e"
            )

            line = self.line(code=line_code, name=line_name, company=company, mode="warp", colour=line_colour)

            builder = self.builder(line)
            for result in search_all(re.compile(r"\|-\n\|(?!<s>)(?P<code>.*?)\n\|(?P<name>.*?)\n"), wiki):
                code = result.group("code").upper()
                if code.startswith("BLUTRAIN"):
                    continue
                codes = {
                    "IKA": {"UIK"},
                    "SPN": {"FDR"},
                    "ILI": {"ITC"},
                    **({"MCN": {"MUR"}} if line_code == "12" else {}),
                }.get(code, {code})
                name = result.group("name").strip()
                if name == "":
                    continue
                builder.add(self.station(codes=codes, name=name, company=company))

            
            builder.connect()
