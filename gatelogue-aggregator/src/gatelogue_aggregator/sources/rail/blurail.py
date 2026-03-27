import re
from concurrent.futures import ThreadPoolExecutor

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import get_json, get_wiki_link, get_wiki_text
from gatelogue_aggregator.source import RailSource


class BluRail(RailSource):
    name = "MRT Wiki (Rail, BluRail)"
    line_wikis: dict[str, str]

    def prepare(self, config: Config):
        line_list = (
            get_json(
                "https://wiki.minecartrapidtransit.net/api.php?action=query&list=categorymembers&cmtitle=Category%3ABluRail+lines&cmlimit=5000&format=json",
                "blurail_line_list",
                config,
            )
        )["query"]["categorymembers"]

        line_codes = [result["title"].removesuffix(" (BluRail line)") for result in line_list]

        def retrieve_line(line_code: str) -> str | None:
            wiki = get_wiki_text(f"{line_code} (BluRail line)", config)
            if "is a planned [[BluRail]] warp train line" in wiki:
                return None
            return wiki

        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            self.line_wikis = {
                k: v for k, v in zip(line_codes, executor.map(retrieve_line, line_codes), strict=False) if v is not None
            }

    def build(self, config: Config):
        company = self.company(name="BluRail", link=get_wiki_link("BluRail"))

        for line_code, wiki in self.line_wikis.items():
            line_name: str = re.search(r"\| linelong = (.*)\n", wiki).group(1)  # pyrefly: ignore [missing-attribute]

            line_colour = (
                "#c01c22"
                if line_code.endswith("X") and line_code[0].isdigit()
                else "#0a7ec3"
                if line_code[-1].isdigit()
                else "#0c4a9e"
            )

            line = self.line(code=line_code, name=line_name, company=company, mode="warp", colour=line_colour)

            builder = self.builder(line)
            for result in re.finditer(re.compile(r"\|-\n\|(?!<s>)(?P<code>.*?)\n\|(?P<name>.*?)\n"), wiki):
                code: str = result.group("code").upper()
                if code.startswith("BLUTRAIN"):
                    continue
                codes = {
                    "IKA": {"UIK"},
                    "SPN": {"FDR"},
                    "ILI": {"ITC"},
                    **({"MCN": {"MUR"}} if line_code == "12" else {}),
                    **({"NFD": {"NFD15"}} if line_code == "15" else {}),
                }.get(code, {code})
                name = result.group("name").strip()
                if name == "":
                    continue
                builder.add(self.station(codes=codes, name=name, company=company))

            builder.connect()
