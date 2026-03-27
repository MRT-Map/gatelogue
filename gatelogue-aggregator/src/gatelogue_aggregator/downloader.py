from __future__ import annotations

import tempfile
import time
from datetime import timedelta
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import msgspec
import msgspec.json
import pandas as pd
import rich
import rich.status
from bs4 import BeautifulSoup
from rnet import Emulation
from rnet.blocking import Client, Response
from rnet.redirect import Policy

from gatelogue_aggregator.logging import ERROR, INFO3, progress_bar

if TYPE_CHECKING:
    from gatelogue_aggregator.config import Config

DEFAULT_TIMEOUT = 60
DEFAULT_COOLDOWN = 15
DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "gatelogue"
DEFAULT_CACHE_DURATION = 3600

SESSION = Client(redirect=Policy.limited(10), emulation=Emulation.Chrome145)

COOLDOWN_LOCK = Lock()
COOLDOWN: dict[str, float] = {}


def _get_url(
    url: str,
    config: Config,
    *,
    etag: bytes | None = None,
    empty_is_error: bool = False,
) -> Response:
    with progress_bar(INFO3, f"  Downloading {url}"):
        netloc = urlparse(url).netloc
        with COOLDOWN_LOCK:
            cond = netloc in COOLDOWN and time.time() < (cool := COOLDOWN[netloc])
        if cond:
            rich.print(INFO3 + f"Waiting for {url} cooldown")
            time.sleep(abs(cool - time.time()))

        headers = {"If-None-Match": etag.decode()} if etag is not None else {}
        response = SESSION.get(url, timeout=timedelta(seconds=config.timeout), headers=headers)

        if response.status.as_int() >= 400 or (empty_is_error and response.text == ""):
            rich.print(ERROR + f"Received {response.status} error from {url}:\n{response.text}")
            if response.status.as_int() in (408, 429):
                with COOLDOWN_LOCK:
                    COOLDOWN[netloc] = time.time() + DEFAULT_COOLDOWN
                rich.print(ERROR + f"Will try {url} again in 15s")
                return _get_url(url, config, empty_is_error=empty_is_error)

        return response


def _deconstruct_response(response: Response):
    text = response.text("utf-8")
    etag = response.headers.get("etag", None)
    return text, etag


def get_url(
    url: str,
    key: str,
    config: Config,
    *,
    empty_is_error: bool = False,
) -> str:
    cache = config.cache_dir / key
    etag_path = config.cache_dir / (key + ".etag")
    until_path = config.cache_dir / (key + ".until")

    etag = etag_path.read_bytes() if etag_path.exists() else None
    until = float(until_path.read_text()) if until_path.exists() else None

    if not cache.exists():
        response = _get_url(url, config, empty_is_error=empty_is_error)
        text, etag = _deconstruct_response(response)
    elif until is not None and until > time.time():
        text = cache.read_text()
        rich.print(INFO3 + f"Reading {url} from {cache}")
    elif etag is not None:
        rich.print(INFO3 + f"Checking etag {etag} for {url} and cache {cache}")
        response = _get_url(url, config, etag=etag, empty_is_error=empty_is_error)
        if response.status.as_int() == 304:
            text = cache.read_text()
            rich.print(INFO3 + f"No change to {url} at cache {cache}")
        else:
            text, etag = _deconstruct_response(response)
            rich.print(INFO3 + f"Change detected at {url} at cache {cache} with etag {etag}")
    else:
        response = _get_url(url, config, empty_is_error=empty_is_error)
        text, etag = _deconstruct_response(response)

    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.touch()
    cache.write_text(text)
    rich.print(INFO3 + f"Saved {url} to cache {cache}")

    if until is None or until <= time.time():
        until = time.time() + config.cache_duration
    if etag is not None:
        etag_path.touch()
        etag_path.write_bytes(etag)
    if until is not None:
        until_path.touch()
        until_path.write_text(str(until))
    return text


def get_json(url: str, key: str, config: Config) -> dict:
    text = get_url(url, key, config, empty_is_error=True)
    try:
        return msgspec.json.decode(text)
    except msgspec.DecodeError as e:
        rich.print(ERROR + f"Received invalid JSON from {url}:\n{e}\n{text}")
        with COOLDOWN_LOCK:
            COOLDOWN[urlparse(url).netloc] = time.time() + DEFAULT_COOLDOWN
        rich.print(ERROR + f"Will try {url} again in 15s")
        return get_json(url, key, config)


def get_csv(url: str, key: str, config: Config, **pd_kwargs) -> pd.DataFrame:
    get_url(url, key, config)
    return pd.read_csv(config.cache_dir / key, **pd_kwargs)


def get_wiki_text(page: str, config: Config, old_id: int | None = None) -> str:
    key = "wiki-text/" + (page.replace("/", "") if old_id is None else str(old_id))
    if old_id is None:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&prop=wikitext&formatversion=2&format=json&page={page}"
    else:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&prop=wikitext&formatversion=2&format=json&oldid={old_id}"
    response = get_url(url, key, config)
    try:
        return msgspec.json.decode(response)["parse"]["wikitext"]
    except Exception as e:
        raise ValueError(response) from e


def get_wiki_html(page: str, config: Config, old_id: int | None = None) -> BeautifulSoup:
    key = "wiki-html/" + (page.replace("/", "") if old_id is None else str(old_id))
    if old_id is None:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&formatversion=2&format=json&page={page}"
    else:
        url = f"https://wiki.minecartrapidtransit.net/api.php?action=parse&formatversion=2&format=json&oldid={old_id}"
    response = get_url(url, key, config)
    try:
        return BeautifulSoup(msgspec.json.decode(response)["parse"]["text"], features="html.parser")
    except Exception as e:
        raise ValueError(response) from e


def get_wiki_link(page: str) -> str:
    return f"https://wiki.minecartrapidtransit.net/index.php/{page}"
