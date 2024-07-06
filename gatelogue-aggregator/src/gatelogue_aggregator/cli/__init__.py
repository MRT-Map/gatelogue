from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
import msgspec.json
import rich
import rich.progress

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import INFO1
from gatelogue_aggregator.sources.air.dynmap_airports import DynmapAirports
from gatelogue_aggregator.sources.air.mrt_transit import MRTTransit
from gatelogue_aggregator.sources.air.wiki_airline import WikiAirline
from gatelogue_aggregator.sources.air.wiki_airport import WikiAirport
from gatelogue_aggregator.sources.bus.intrabus import IntraBus
from gatelogue_aggregator.sources.bus.intrabus_warp import IntraBusWarp
from gatelogue_aggregator.sources.rail.blurail import BluRail
from gatelogue_aggregator.sources.rail.blurail_warp import BluRailWarp
from gatelogue_aggregator.sources.rail.dynmap_mrt import DynmapMRT
from gatelogue_aggregator.sources.rail.intrarail import IntraRail
from gatelogue_aggregator.sources.rail.intrarail_local import IntraRailLocal
from gatelogue_aggregator.sources.rail.intrarail_mcr_warp import IntraRailMCRWarp
from gatelogue_aggregator.sources.rail.intrarail_warp import IntraRailWarp
from gatelogue_aggregator.sources.rail.marblerail import MarbleRail
from gatelogue_aggregator.sources.rail.marblerail_warp import MarbleRailWarp
from gatelogue_aggregator.sources.rail.nflr import NFLR
from gatelogue_aggregator.sources.rail.nflr_warp import NFLRWarp
from gatelogue_aggregator.sources.rail.railinq import RaiLinQ
from gatelogue_aggregator.sources.rail.railinq_warp import RaiLinQWarp
from gatelogue_aggregator.sources.rail.wiki_mrt import WikiMRT
from gatelogue_aggregator.sources.rail.wzr import WZR
from gatelogue_aggregator.sources.rail.wzr_warp import WZRWarp
from gatelogue_aggregator.sources.sea.aqualinq import AquaLinQ
from gatelogue_aggregator.sources.sea.aqualinq_warp import AquaLinQWarp
from gatelogue_aggregator.sources.sea.hbl import HBL
from gatelogue_aggregator.sources.sea.hbl_warp import HBLWarp
from gatelogue_aggregator.sources.sea.intrasail import IntraSail
from gatelogue_aggregator.sources.sea.intrasail_warp import IntraSailWarp
from gatelogue_aggregator.sources.sea.wzf import WZF
from gatelogue_aggregator.sources.sea.wzf_warp import WZFWarp
from gatelogue_aggregator.sources.town import TownList
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.context import Context


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(version=__version__, prog_name="gatelogue-aggregator")
def gatelogue_aggregator():
    pass


@gatelogue_aggregator.command(help="actually run the aggregator")
@click.option(
    "--cache-dir",
    default=DEFAULT_CACHE_DIR,
    type=Path,
    show_default=True,
    help="where to cache files downloaded from the Internet (preferably a temporary directory)",
)
@click.option(
    "--timeout",
    default=DEFAULT_TIMEOUT,
    type=int,
    show_default=True,
    help="how long to wait for a network request in seconds before aborting and failing",
)
@click.option(
    "-o", "--output", default="data.json", type=Path, show_default=True, help="file to output the result to, in JSON"
)
@click.option("-f/", "--fmt/--no-fmt", default=False, show_default=True, help="prettify the JSON result")
@click.option(
    "-g",
    "--graph",
    type=Path,
    default=None,
    show_default=True,
    help="file to output a graph representation of all nodes and objects to, in SVG",
)
@click.option(
    "-w",
    "--max_workers",
    type=int,
    default=8,
    show_default=True,
    help="maximum number of concurrent workers that download and process data",
)
@click.option(
    "-e",
    "--cache-exclude",
    type=str,
    default="",
    show_default=True,
    help="re-retrieve data for these sources instead of loading from cache (separate with `;`, use `*` for all sources)",
)
def run(
    *, cache_dir: Path, timeout: int, output: Path, fmt: bool, graph: Path | None, max_workers: int, cache_exclude: str
):
    sources = [
        MRTTransit,
        DynmapAirports,
        WikiAirline,
        WikiAirport,
        BluRail,
        BluRailWarp,
        IntraRail,
        IntraRailLocal,
        IntraRailWarp,
        IntraRailMCRWarp,
        RaiLinQ,
        RaiLinQWarp,
        WZR,
        WZRWarp,
        WikiMRT,
        DynmapMRT,
        AquaLinQ,
        AquaLinQWarp,
        HBL,
        HBLWarp,
        IntraSail,
        IntraSailWarp,
        WZF,
        WZFWarp,
        IntraBus,
        IntraBusWarp,
        TownList,
        NFLR,
        NFLRWarp,
        MarbleRail,
        MarbleRailWarp,
    ]
    cache_exclude = [c.__name__ for c in sources] if cache_exclude == "*" else cache_exclude.split(";")
    config = Config(
        cache_dir=cache_dir,
        timeout=timeout,
        cache_exclude=cache_exclude,
    )
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        result = list(executor.map(lambda s: s(config), sources))
    ctx = Context.from_sources(result)
    if graph is not None:
        ctx.graph(graph)
    j = msgspec.json.encode(ctx.ser())
    if fmt:
        rich.print(INFO1 + f"Outputting to {output} (formatted)")
        output.write_text(msgspec.json.format(j.decode("utf-8")))
    else:
        rich.print(INFO1 + f"Outputting to {output} (unformatted)")
        output.write_bytes(j)


@gatelogue_aggregator.command(help="export a JSON schema of the current data format")
@click.option(
    "-o", "--output", default="data.json", type=Path, show_default=True, help="file to output the result to, in JSON"
)
@click.option("-f/", "--fmt/--no-fmt", default=False, show_default=True, help="prettify the JSON result")
def schema(output: Path, *, fmt: bool):
    j = msgspec.json.encode(msgspec.json.schema(Context.Ser))
    if fmt:
        rich.print(INFO1 + f"Outputting to {output} (formatted)")
        output.write_text(msgspec.json.format(j.decode("utf-8")))
    else:
        rich.print(INFO1 + f"Outputting to {output} (unformatted)")
        output.write_bytes(j)
