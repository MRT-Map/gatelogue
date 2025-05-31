from __future__ import annotations

import os
from collections.abc import Iterable, Sized

import rich.progress

PROGRESS: rich.progress.Progress = rich.progress.Progress()
PROGRESS.start()

INFO1 = "[yellow]"
INFO2 = "[green]  "
INFO3 = "[dim green]    "
RESULT = "[cyan]  "
ERROR = "[bold red]"


def track[T](
    it: Iterable[T], level: str, *, description: str, nonlinear: bool = False, total: int | None = None
) -> Iterable[T]:
    if os.getenv("NO_PROGRESS_BAR"):
        rich.print(level + description)
        yield from it
    else:
        total = total or (((len(it) ** 2) / 2 if nonlinear else len(it)) if isinstance(it, Sized) else None)
        t = PROGRESS.add_task(level + description, total=total)
        for i, o in enumerate(it):
            yield o
            PROGRESS.advance(t, i + 1 if nonlinear else 1)
        PROGRESS.remove_task(t)

    rich.print(level + description + " done")
