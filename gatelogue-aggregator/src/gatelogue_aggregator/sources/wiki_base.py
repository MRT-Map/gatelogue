from pathlib import Path

import msgspec.json
from bs4 import BeautifulSoup

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url


def get_wiki_text(
    page: str, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT, old_id: int | None = None
) -> str:
    cache = cache_dir / "wiki-text" / (page if old_id is None else str(old_id))
    if old_id is None:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&prop=wikitext&formatversion=2&format=json&page={page}"
    else:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&prop=wikitext&formatversion=2&format=json&oldid={old_id}"
    response = get_url(url, cache, timeout)
    try:
        return msgspec.json.decode(response)["parse"]["wikitext"]
    except Exception as e:
        raise ValueError(response[:100]) from e


def get_wiki_html(
    page: str, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT, old_id: int | None = None
) -> BeautifulSoup:
    cache = cache_dir / "wiki-html" / (page if old_id is None else str(old_id))
    if old_id is None:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&formatversion=2&format=json&page={page}"
    else:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&formatversion=2&format=json&oldid={old_id}"
    response = get_url(url, cache, timeout)
    try:
        return BeautifulSoup(msgspec.json.decode(response)["parse"]["text"], features="html.parser")
    except Exception as e:
        raise ValueError(response[:100]) from e


def get_wiki_link(page: str) -> str:
    return f"https://wiki.minecartrapidtransit.net/index.php/{page}"
