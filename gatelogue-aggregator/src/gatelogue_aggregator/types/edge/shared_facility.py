from __future__ import annotations

from pathlib import Path

import msgspec
import rich

from gatelogue_aggregator.logging import ERROR
from gatelogue_aggregator.types.source import Source


class SharedFacility(msgspec.Struct):
    pass


class Yaml(msgspec.Struct):
    c1: str
    c2: str
    s1: str = ""
    s2: str = ""
    code1: str | None = None
    code2: str | None = None


class SharedFacilitySource(Source):
    name = "Gatelogue"
    priority = 0

    def update(self):
        from gatelogue_aggregator.types.node.rail import RailCompany, RailStation

        with (Path(__file__).parent / "shared_facilities.yaml").open() as f:
            file = msgspec.yaml.decode(f.read(), type=list[Yaml])

        nonexistent_companies = set()
        for entry in file:
            station1 = next(
                (
                    a
                    for a in self.g.nodes()
                    if isinstance(a, RailStation)
                    and (
                        (entry.code1 is not None and entry.code1 in a.codes)
                        or (a.name is not None and a.name.v.strip() == entry.s1)
                    )
                    and a.get_one(self, RailCompany).name == entry.c1
                ),
                None,
            )
            station2 = next(
                (
                    a
                    for a in self.g.nodes()
                    if isinstance(a, RailStation)
                    and (
                        (entry.code2 is not None and entry.code2 in a.codes)
                        or (a.name is not None and a.name.v.strip() == entry.s2)
                    )
                    and a.get_one(self, RailCompany).name == entry.c2
                ),
                None,
            )

            if station1 is None:
                if entry.c1 in nonexistent_companies:
                    pass
                elif len(self.g.filter_nodes(lambda a: isinstance(a, RailCompany) and a.name == entry.c1)) == 0:
                    rich.print(ERROR + f"Company {entry.c1} does not exist")
                    nonexistent_companies.add(entry.c1)
                else:
                    rich.print(ERROR + f"{entry.c1} {entry.s1} does not exist")
                continue
            if station2 is None:
                if entry.c2 in nonexistent_companies:
                    pass
                elif len(self.g.filter_nodes(lambda a: isinstance(a, RailCompany) and a.name == entry.c2)) == 0:
                    rich.print(ERROR + f"Company {entry.c2} does not exist")
                    nonexistent_companies.add(entry.c2)
                else:
                    rich.print(ERROR + f"{entry.c2} {entry.s2} does not exist")
                continue
            station1.connect(self, station2, SharedFacility())
