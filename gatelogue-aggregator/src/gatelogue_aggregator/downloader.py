import contextlib
import tempfile
import uuid
from collections.abc import Iterator
from pathlib import Path

import msgspec
import requests
import rich
import rich.status

from gatelogue_aggregator.logging import PROGRESS, INFO2, INFO3

DEFAULT_TIMEOUT = 60
DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "gatelogue"


def get_url(url: str, cache: Path, timeout: int = DEFAULT_TIMEOUT) -> str:
    if cache.exists():
        rich.print(INFO3 + f"Reading {url} from {cache}")
        return cache.read_text()
    task = PROGRESS.add_task(f"  Downloading {url}", total=None)
    response = requests.get(url, timeout=timeout).text
    with contextlib.suppress(UnicodeEncodeError, UnicodeDecodeError):
        response = response.encode("latin").decode("utf-8")
    PROGRESS.remove_task(task)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.touch()
    cache.write_text(response)
    rich.print(INFO3 + f"Downloaded {url} to {cache}")
    return response


def warps(player: uuid.UUID, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT) -> Iterator[dict]:
    link = f"https://api.minecartrapidtransit.net/api/v1/warps?player={player}"
    offset = 0
    ls: list[dict] = msgspec.json.decode(get_url(link, cache_dir / "mrt-api" / str(player) / str(offset), timeout))
    while len(ls) != 0:
        yield from ls
        offset += len(ls)
        ls = msgspec.json.decode(
            get_url(link + f"&offset={offset}", cache_dir / "mrt-api" / str(player) / str(offset), timeout)
        )
