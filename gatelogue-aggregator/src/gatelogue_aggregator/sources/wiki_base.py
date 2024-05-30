from pathlib import Path

import msgspec.json

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_TIMEOUT, get_url


def get_wikitext(page: str, cache_dir: Path = DEFAULT_CACHE_DIR, timeout: int = DEFAULT_TIMEOUT) -> str:
    cache = cache_dir / "wiki" / page
    url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&prop=wikitext&formatversion=2&format=json&page={page}"
    response = get_url(url, cache, timeout)
    return msgspec.json.decode(response)["parse"]["wikitext"]
