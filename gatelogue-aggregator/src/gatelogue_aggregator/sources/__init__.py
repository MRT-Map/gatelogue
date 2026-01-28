from __future__ import annotations

from typing import TYPE_CHECKING

from gatelogue_aggregator.sources.sea import SOURCES as SOURCES_SEA

if TYPE_CHECKING:
    from gatelogue_aggregator.source import Source


def SOURCES() -> list[type[Source]]:  # noqa: N802

    return [
        *SOURCES_SEA()
    ]
