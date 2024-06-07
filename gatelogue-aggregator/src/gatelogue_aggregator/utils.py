from __future__ import annotations

from typing import TYPE_CHECKING

import rich.progress

if TYPE_CHECKING:
    import re
    from collections.abc import Iterator


def search_all(regex: re.Pattern[str], text: str) -> Iterator[re.Match[str]]:
    pos = 0
    while (match := regex.search(text, pos)) is not None:
        pos = match.end()
        yield match


PROGRESS: rich.progress.Progress = rich.progress.Progress(transient=True)
PROGRESS.start()
