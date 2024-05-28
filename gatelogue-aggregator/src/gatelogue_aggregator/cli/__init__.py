import click

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.sources.mrt_transit import MRTTransit


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="gatelogue-aggregator")
def gatelogue_aggregator():
    click.echo("Hello world!")
    MRTTransit()
