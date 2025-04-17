from __future__ import annotations

import contextlib
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import cloudscraper
import msgspec
import rich
import rich.status

from gatelogue_aggregator.logging import ERROR, INFO3, PROGRESS

if TYPE_CHECKING:
    import uuid
    from collections.abc import Iterator

    from gatelogue_aggregator.types.config import Config

DEFAULT_TIMEOUT = 60
DEFAULT_COOLDOWN = 15
DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "gatelogue"

SESSION = cloudscraper.create_scraper()
COOLDOWN: dict[str, float] = {}


def get_url(url: str, cache: Path, timeout: int = DEFAULT_TIMEOUT, cooldown: int = DEFAULT_COOLDOWN) -> str:
    if cache.exists():
        rich.print(INFO3 + f"Reading {url} from {cache}")
        return cache.read_text()
    task = PROGRESS.add_task(INFO3 + f"  Downloading {url}", total=None)

    netloc = urlparse(url).netloc
    if netloc in COOLDOWN and time.time() < (cool := COOLDOWN[netloc]):
        rich.print(INFO3 + f"Waiting for {url} cooldown")
        time.sleep(abs(cool - time.time()))

    response = SESSION.get(url, timeout=timeout)
    if response.status_code >= 400:  # noqa: PLR2004
        rich.print(ERROR + f"Received {response.status_code} error from {url}:\n{response.text}")
        if response.status_code == 429:  # noqa: PLR2004
            COOLDOWN[netloc] = time.time() + DEFAULT_COOLDOWN
            rich.print(ERROR + f"Will try {url} again in 15s")
            return get_url(url, cache, timeout, cooldown)

    text = response.text
    with contextlib.suppress(UnicodeEncodeError, UnicodeDecodeError):
        text = text.encode("latin").decode("utf-8")
    PROGRESS.remove_task(task)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.touch()
    cache.write_text(text)
    rich.print(INFO3 + f"Downloaded {url} to {cache}")
    return text


def warps(player: uuid.UUID, config: Config) -> Iterator[dict]:
    link = f"https://api.minecartrapidtransit.net/api/v2/warps?player={player}"
    offset = 0
    ls: list[dict] = msgspec.json.decode(
        get_url(link, config.cache_dir / "mrt-api" / str(player) / str(offset), config.timeout, config.cooldown)
    )["result"]
    while len(ls) != 0:
        yield from ls
        offset += len(ls)
        ls = msgspec.json.decode(
            get_url(
                link + f"&offset={offset}",
                config.cache_dir / "mrt-api" / str(player) / str(offset),
                config.timeout,
                config.cooldown,
            )
        )["result"]


def all_warps(config: Config) -> Iterator[dict]:
    link = "https://api.minecartrapidtransit.net/api/v2/warps"
    offset = 0
    ls: list[dict] = msgspec.json.decode(
        get_url(link, config.cache_dir / "mrt-api" / "all" / str(offset), config.timeout, config.cooldown)
    )["result"]
    while len(ls) != 0:
        yield from ls
        offset += len(ls)
        ls = msgspec.json.decode(
            get_url(
                link + f"?offset={offset}",
                config.cache_dir / "mrt-api" / "all" / str(offset),
                config.timeout,
                config.cooldown,
            )
        )["result"]
