import uuid
from pathlib import Path

import click
import msgspec.json
import rich

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.air.dynmap_airports import DynmapAirports
from gatelogue_aggregator.sources.air.mrt_transit import MRTTransit
from gatelogue_aggregator.sources.air.wiki_airline import WikiAirline
from gatelogue_aggregator.sources.air.wiki_airport import WikiAirport
from gatelogue_aggregator.sources.rail.blurail import BluRail
from gatelogue_aggregator.sources.rail.dynmap_mrt import DynmapMRT
from gatelogue_aggregator.sources.rail.intrarail import IntraRail
from gatelogue_aggregator.sources.rail.railinq import RaiLinQ
from gatelogue_aggregator.sources.rail.wiki_mrt import WikiMRT
from gatelogue_aggregator.types.context import Context


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="gatelogue-aggregator")
def gatelogue_aggregator():
    click.echo(click.get_current_context().get_help())


@gatelogue_aggregator.command()
@click.option("--cache-dir", default=DEFAULT_CACHE_DIR, type=Path, show_default=True)
@click.option("--timeout", default=DEFAULT_TIMEOUT, type=int, show_default=True)
@click.option("-o", "--output", default="data.json", type=Path, show_default=True)
@click.option("-f/", "--fmt/--no-fmt", default=False, show_default=True)
@click.option("-g", "--graph", type=Path, default=None, show_default=True)
def run(*, cache_dir: Path, timeout: int, output: Path, fmt: bool, graph: Path | None):
    ctx = Context.from_sources(
        [
            MRTTransit(cache_dir, timeout),
            DynmapAirports(cache_dir, timeout),
            WikiAirline(cache_dir, timeout),
            WikiAirport(cache_dir, timeout),
            BluRail(cache_dir, timeout),
            IntraRail(cache_dir, timeout),
            RaiLinQ(cache_dir, timeout),
            WikiMRT(cache_dir, timeout),
            DynmapMRT(cache_dir, timeout),
        ]
    )
    if graph is not None:
        ctx.graph(graph)
    j = msgspec.json.encode(ctx.ser())
    if fmt:
        rich.print(f"[yellow]Outputting to {output} (formatted)")
        output.write_text(msgspec.json.format(j.decode("utf-8")))
    else:
        rich.print(f"[yellow]Outputting to {output} (unformatted)")
        output.write_bytes(j)
