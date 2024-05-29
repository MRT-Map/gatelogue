import base64

import click
import msgspec.json

from gatelogue_aggregator.__about__ import __version__
from gatelogue_aggregator.sources.dynmap_airports import DynmapAirports
from gatelogue_aggregator.sources.mrt_transit import MRTTransit
from gatelogue_aggregator.types.context import Context


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="gatelogue-aggregator")
def gatelogue_aggregator():
    ctx = Context.from_sources([MRTTransit(), DynmapAirports()])
    j = msgspec.json.encode(ctx.dict())
    with open("test.json", "w") as f:
        f.write(msgspec.json.format(base64.b64decode(msgspec.json.encode(j)).decode()))
