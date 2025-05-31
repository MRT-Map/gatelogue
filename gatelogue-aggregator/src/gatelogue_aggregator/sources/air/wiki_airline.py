from __future__ import annotations

from typing import TYPE_CHECKING

import rich.progress

from gatelogue_aggregator.logging import ERROR, INFO2, RESULT, track
from gatelogue_aggregator.sources.air.wiki_extractors.airline import _EXTRACTORS
from gatelogue_aggregator.sources.wiki_base import get_wiki_link, get_wiki_text
from gatelogue_aggregator.types.node.air import AirAirline, AirAirport, AirFlight, AirGate, AirSource
from gatelogue_aggregator.types.source import Source
from gatelogue_aggregator.utils import search_all

if TYPE_CHECKING:
    from collections.abc import Callable
    from re import Pattern

    from gatelogue_aggregator.types.config import Config


class WikiAirline(AirSource):
    name = "MRT Wiki (Airline)"
    priority = 1

    def build(self, config: Config):
        for airline in track(_EXTRACTORS, description=INFO2 + "Extracting data from wikipages"):
            airline(self, config)
        

    def regex_extract_airline(
        self,
        airline_name: str,
        page_name: str,
        regex: Pattern[str],
        config: Config,
        size: str | Callable[[dict[str, str]], str] | None = None,
    ) -> AirAirline:
        wikitext = get_wiki_text(page_name, config)
        airline = self.extract_get_airline(airline_name, page_name)
        result = 0
        for match in search_all(regex, wikitext):
            matches = match.groupdict()
            if size is not None:
                matches["s"] = size if isinstance(size, str) else size(matches)
            self.extract_get_flight(airline, **matches)
            result += 1
        if not result:
            rich.print(ERROR + f"Extraction for {airline_name} yielded no results")
        else:
            rich.print(RESULT + f"{airline_name} has {result} flights")
        return airline

    def extract_get_airline(self, airline_name: str, page_name: str) -> AirAirline:
        return AirAirline.new(self, name=AirAirline.process_airline_name(airline_name), link=get_wiki_link(page_name))

    def extract_get_flight(
        self,
        airline: AirAirline,
        *,
        code: str,
        a1: str | None = None,
        a2: str | None = None,
        a3: str | None = None,
        a12: str | None = None,
        a22: str | None = None,
        a32: str | None = None,
        g1: str | None = None,
        g2: str | None = None,
        g3: str | None = None,
        s: str | None = None,
        **_,
    ) -> AirFlight:
        f = AirFlight.new(self, codes=AirFlight.process_code(code, airline.name), airline=airline)

        airport1 = AirAirport.process_code(a1 or a12)
        gate_code1 = AirGate.process_code(g1, airline.name, airport1)
        gate1 = AirGate.new(
            self,
            code=gate_code1,
            airport=AirAirport.new(self, code=airport1),
            size=str(s) if s is not None and gate_code1 is not None else None,
        )
        f.connect(self, gate1)
        if gate_code1 is not None:
            airline.connect(self, gate1)

        airport2 = AirAirport.process_code(a2 or a22)
        gate_code2 = AirGate.process_code(g2, airline.name, airport2)
        gate2 = AirGate.new(
            self,
            code=gate_code2,
            airport=AirAirport.new(self, code=airport2),
            size=str(s) if s is not None and gate_code2 is not None else None,
        )
        f.connect(
            self,
            gate2,
        )
        if gate_code2 is not None:
            airline.connect(self, gate2)

        if (a3 is not None or a32 is not None) and g3 is not None:
            airport3 = AirAirport.process_code(a3 or a32)
            gate_code3 = AirGate.process_code(g3, airline.name, airport3)
            gate3 = AirGate.new(
                self,
                code=gate_code3,
                airport=AirAirport.new(self, code=airport3),
                size=str(s) if s is not None and gate_code3 is not None else None,
            )
            f.connect(self, gate3)
            if gate_code3 is not None:
                airline.connect(self, gate3)
        return f
