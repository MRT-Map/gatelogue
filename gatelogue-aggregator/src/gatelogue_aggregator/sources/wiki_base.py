from pathlib import Path

import msgspec.json

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url


def get_wiki_text(page: str, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT) -> str:
    cache = cache_dir / "wiki" / page
    url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&prop=wikitext&formatversion=2&format=json&page={page}"
    response = get_url(url, cache, timeout)
    try:
        return msgspec.json.decode(response)["parse"]["wikitext"]
    except Exception as e:
        raise ValueError(response[:100]) from e


def get_wiki_link(page: str) -> str:
    return f"https://wiki.minecartrapidtransit.net/index.php/{page}"
