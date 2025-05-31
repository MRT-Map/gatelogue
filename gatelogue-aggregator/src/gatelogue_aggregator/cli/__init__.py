from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
import gatelogue_types as gt
import msgspec.json
import rich
import rich.progress

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_COOLDOWN, DEFAULT_TIMEOUT
from gatelogue_aggregator.logging import INFO1, PROGRESS
from gatelogue_aggregator.sources import SOURCES
from gatelogue_aggregator.types.config import Config
from gatelogue_aggregator.types.gatelogue_data import GatelogueData
from gatelogue_aggregator.types.source import Source


def _enc_hook(obj):
    if isinstance(obj, type) and issubclass(obj, Source):
        return str(obj)
    raise NotImplementedError(obj)


def _schema_hook(obj):
    if isinstance(obj, type):
        return msgspec.json.schema(str)
    raise NotImplementedError


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
    "--cooldown",
    default=DEFAULT_COOLDOWN,
    type=int,
    show_default=True,
    help="how long to wait before sending new requests to the same URL if `429 Too Many Requests` is received",
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
    "-ce",
    "--cache-exclude",
    type=str,
    default="",
    show_default=True,
    help="re-retrieve data for these sources instead of loading from cache (separate with `;`, use `*` for all sources)",
)
@click.option(
    "-i",
    "--include",
    type=str,
    default="",
    show_default=True,
    help="sources to retrieve from (do not use with --exclude) (separate with `;`, use `*` for all sources)",
)
@click.option(
    "-e",
    "--exclude",
    type=str,
    default="",
    show_default=True,
    help="sources NOT to retrieve from (do not use with --include) (separate with `;`, use `*` for all sources)",
)
def run(
    *,
    cache_dir: Path,
    timeout: int,
    cooldown: int,
    output: Path,
    fmt: bool,
    graph: Path | None,
    max_workers: int,
    cache_exclude: str,
    include: str,
    exclude: str,
):
    if include and exclude:
        raise click.BadOptionUsage("--include/--exclude", "cannot use --include and --exclude at the same time")  # noqa: EM101

    sources = [
        a
        for a in SOURCES()
        if (not include and not exclude)
        or (include and (include == "*" or a.__name__ in include.split(";")))
        or (exclude and (exclude != "*" and a.__name__ not in exclude.split(";")))
    ]
    cache_exclude = [c.__name__ for c in sources] if cache_exclude == "*" else cache_exclude.split(";")

    config = Config(
        cache_dir=cache_dir, timeout=timeout, cooldown=cooldown, cache_exclude=cache_exclude, max_workers=max_workers
    )
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        result = list(executor.map(lambda s: s(config), sources))

    src = GatelogueData.from_sources(result)

    if graph is not None:
        task = PROGRESS.add_task(INFO1 + f"Outputting graph to {graph}... ", total=None)
        src.graph(graph)
        PROGRESS.remove_task(task)

    task = PROGRESS.add_task(INFO1 + "Exporting to JSON... ", total=None)
    j = msgspec.json.encode(src.export(), enc_hook=_enc_hook)
    PROGRESS.remove_task(task)
    if fmt:
        rich.print(INFO1 + f"Writing to {output} (formatted)")
        output.write_text(msgspec.json.format(j.decode("utf-8")))
    else:
        rich.print(INFO1 + f"Writing to {output} (unformatted)")
        output.write_bytes(j)


@gatelogue_aggregator.command(help="export a JSON schema of the current data format")
@click.option(
    "-o", "--output", default="data.json", type=Path, show_default=True, help="file to output the result to, in JSON"
)
@click.option("-f/", "--fmt/--no-fmt", default=False, show_default=True, help="prettify the JSON result")
def schema(output: Path, *, fmt: bool):
    j = msgspec.json.encode(msgspec.json.schema(gt.GatelogueData, schema_hook=_schema_hook))
    if fmt:
        rich.print(INFO1 + f"Outputting to {output} (formatted)")
        output.write_text(msgspec.json.format(j.decode("utf-8")))
    else:
        rich.print(INFO1 + f"Outputting to {output} (unformatted)")
        output.write_bytes(j)
