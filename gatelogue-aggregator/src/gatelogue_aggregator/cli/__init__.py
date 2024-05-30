from pathlib import Path

import click
import msgspec.json
import rich

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT
from gatelogue_aggregator.sources.dynmap_airports import DynmapAirports
from gatelogue_aggregator.sources.mrt_transit import MRTTransit
from gatelogue_aggregator.sources.wiki_airline import WikiAirline
from gatelogue_aggregator.sources.wiki_airport import WikiAirport
from gatelogue_aggregator.types.context import Context


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--cache-dir", default=DEFAULT_CACHE_DIR, type=Path, show_default=True)
@click.option("--timeout", default=DEFAULT_TIMEOUT, type=int, show_default=True)
@click.option("-o", "--output", default="out.json", type=Path, show_default=True)
@click.option("-f/", "--fmt/--no-fmt", default=False, show_default=True)
@click.version_option(version=__version__, prog_name="gatelogue-aggregator")
def gatelogue_aggregator(*, cache_dir: Path, timeout: int, output: Path, fmt: bool):
    ctx = Context.from_sources(
        [
            MRTTransit(cache_dir, timeout),
            DynmapAirports(cache_dir, timeout),
            WikiAirline(cache_dir, timeout),
            WikiAirport(cache_dir, timeout),
        ]
    )
    j = msgspec.json.encode(ctx.dict())
    if fmt:
        rich.print(f"[yellow]Outputting to {output} (formatted)")
        output.write_text(msgspec.json.format(j.decode()))
    else:
        rich.print(f"[yellow]Outputting to {output} (unformatted)")
        output.write_bytes(j)
