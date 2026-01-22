from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from gatelogue_aggregator.downloader import DEFAULT_CACHE_DIR, DEFAULT_COOLDOWN, DEFAULT_TIMEOUT

if TYPE_CHECKING:
    from pathlib import Path


@dataclasses.dataclass
class Config:
    cache_dir: Path = DEFAULT_CACHE_DIR
    timeout: int = DEFAULT_TIMEOUT
    cooldown: int = DEFAULT_COOLDOWN
    cache_exclude: list[str] = dataclasses.field(default_factory=list)
    max_workers: int = 8
