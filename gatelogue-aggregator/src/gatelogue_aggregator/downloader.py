import contextlib
import tempfile
import uuid
from pathlib import Path
from typing import Iterator

import msgspec
import requests
import rich
import rich.status

DEFAULT_TIMEOUT = 60
DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "gatelogue"


def get_url(url: str, cache: Path, timeout: int = DEFAULT_TIMEOUT) -> str:
    if cache.exists():
        rich.print(f"[green]  Reading {url} from {cache}")
        return cache.read_text()
    status = rich.status.Status(f"Downloading {url}")
    status.start()
    response = requests.get(url, timeout=timeout).text
    with contextlib.suppress(UnicodeEncodeError, UnicodeDecodeError):
        response = response.encode("latin").decode("utf-8")
    status.stop()
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.touch()
    cache.write_text(response)
    rich.print(f"[green]  Downloaded {url} to {cache}")
    return response


def warps(player: uuid.UUID, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT) -> Iterator[dict]:
    link = f"https://api.minecartrapidtransit.net/api/v1/warps?player={player}"
    offset = 0
    l: list[dict] = msgspec.json.decode(get_url(link, cache_dir / "mrt-api" / str(player) / str(offset), timeout))
    while len(l) != 0:
        for d in l:
            yield d
        offset += len(l)
        l = msgspec.json.decode(
            get_url(link + f"&offset={offset}", cache_dir / "mrt-api" / str(player) / str(offset), timeout)
        )
