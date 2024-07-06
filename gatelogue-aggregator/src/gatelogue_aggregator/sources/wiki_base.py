from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec.json
from bs4 import BeautifulSoup

from gatelogue_aggregator.downloader import get_url

if TYPE_CHECKING:
    from gatelogue_aggregator.types.config import Config


def get_wiki_text(page: str, config: Config, old_id: int | None = None) -> str:
    cache = config.cache_dir / "wiki-text" / (page if old_id is None else str(old_id))
    if old_id is None:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&prop=wikitext&formatversion=2&format=json&page={page}"
    else:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&prop=wikitext&formatversion=2&format=json&oldid={old_id}"
    response = get_url(url, cache, config.timeout)
    try:
        return msgspec.json.decode(response)["parse"]["wikitext"]
    except Exception as e:
        for a in [response[i:i+100] for i in range(0, len(response), 100)]:
            print(a, end="")
        raise ValueError(response) from e


def get_wiki_html(page: str, config: Config, old_id: int | None = None) -> BeautifulSoup:
    cache = config.cache_dir / "wiki-html" / (page if old_id is None else str(old_id))
    if old_id is None:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&formatversion=2&format=json&page={page}"
    else:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&formatversion=2&format=json&oldid={old_id}"
    response = get_url(url, cache, config.timeout)
    try:
        return BeautifulSoup(msgspec.json.decode(response)["parse"]["text"], features="html.parser")
    except Exception as e:
        raise ValueError(response) from e


def get_wiki_link(page: str) -> str:
    return f"https://wiki.minecartrapidtransit.net/index.php/{page}"
