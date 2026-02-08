from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
import gatelogue_types as gt
import msgspec.json
import rich
import rich.progress

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_COOLDOWN, DEFAULT_TIMEOUT
from gatelogue_aggregator.gatelogue_data import GatelogueData
from gatelogue_aggregator.logging import INFO1, progress_bar, draw_graph
from gatelogue_aggregator.source import Source
from gatelogue_aggregator.sources import SOURCES


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
    "-o", "--output", default="data.db", type=Path, show_default=True, help="file to output the result to, as an SQLite DB"
)
@click.option(
    "-r/-R", "--report/--no-report", default=True, show_default=True, help="print a report of all nodes after merger"
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
    report: bool,
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

    gd = GatelogueData(config, sources)

    if report:
        gd.report()

    if output != Path("/dev/null"):
        rich.print(INFO1 + f"Writing to {output}")
        gd.gd.conn.backup(sqlite3.connect(output))


@gatelogue_aggregator.command(help="create a graph of the DB")
@click.option(
    "-i",
    "--input",
    "input_",
    type=Path,
    default="data.db",
    show_default=True,
    help="path of the SQLite DB",
)
@click.option(
    "-o",
    "--output",
    type=Path,
    default="graph.svg",
    show_default=True,
    help="path to output the SVG graph to",
)
def graph(*, input_: Path, output: Path):
    gd = gt.GD(input_)
    output.write_bytes(draw_graph(gd))

@gatelogue_aggregator.command(help="create a graph of the DB")
@click.option(
    "-i",
    "--input",
    "input_",
    type=Path,
    default="data.db",
    show_default=True,
    help="Path of the SQLite DB",
)
@click.option(
    "-o",
    "--output",
    type=Path,
    default="data-ns.db",
    show_default=True,
    help="patah to output the sourceless DB to",
)
def drop_sources(*, input_: Path, output: Path):
    gd = gt.GD.from_bytes(input_.read_bytes())
    gd.drop_sources()
    gd.conn.commit()
    gd.conn.backup(sqlite3.connect(output))
