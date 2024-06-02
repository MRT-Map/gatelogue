import tempfile
from pathlib import Path

import requests
import rich
import rich.status

DEFAULT_TIMEOUT = 60
DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "gatelogue"


def get_url(url: str, cache: Path, timeout: int = 60) -> str:
    if cache.exists():
        rich.print(f"[green]  Reading {url} from {cache}")
        return cache.read_text()
    status = rich.status.Status(f"Downloading {url}")
    status.start()
    response = requests.get(url, timeout=timeout).text
    try:
        response = response.encode("latin").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    status.stop()
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.touch()
    cache.write_text(response)
    rich.print(f"[green]  Downloaded {url} to {cache}")
    return response
