from __future__ import annotations

import contextlib
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import msgspec
import rich
import rich.status

from gatelogue_aggregator.logging import INFO3, PROGRESS, ERROR

if TYPE_CHECKING:
    import uuid
    from collections.abc import Iterator

    from gatelogue_aggregator.types.config import Config

DEFAULT_TIMEOUT = 60
DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "gatelogue"

SESSION = httpx.Client(http2=True)


def get_url(url: str, cache: Path, timeout: int = DEFAULT_TIMEOUT) -> str:
    if cache.exists():
        rich.print(INFO3 + f"Reading {url} from {cache}")
        return cache.read_text()
    task = PROGRESS.add_task(INFO3 + f"  Downloading {url}", total=None)
    response = SESSION.get(url, timeout=timeout)
    if response.is_error:
        rich.print(ERROR + f"Received {response.status_code} error from {url}:\n{response.text}")

    with contextlib.suppress(UnicodeEncodeError, UnicodeDecodeError):
        text = response.text.encode("latin").decode("utf-8")
    PROGRESS.remove_task(task)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.touch()
    cache.write_text(text)
    rich.print(INFO3 + f"Downloaded {url} to {cache}")
    return text


def warps(player: uuid.UUID, config: Config) -> Iterator[dict]:
    link = f"https://api.minecartrapidtransit.net/api/v1/warps?player={player}"
    offset = 0
    ls: list[dict] = msgspec.json.decode(
        get_url(link, config.cache_dir / "mrt-api" / str(player) / str(offset), config.timeout)
    )
    while len(ls) != 0:
        yield from ls
        offset += len(ls)
        ls = msgspec.json.decode(
            get_url(
                link + f"&offset={offset}", config.cache_dir / "mrt-api" / str(player) / str(offset), config.timeout
            )
        )
