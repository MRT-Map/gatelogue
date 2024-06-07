from __future__ import annotations

from collections.abc import Iterable, Sized

import rich.progress

PROGRESS: rich.progress.Progress = rich.progress.Progress(transient=True)
PROGRESS.start()

INFO1 = "[yellow]"
INFO2 = "[green]  "
INFO3 = "[dim green]    "
RESULT = "[cyan]  "
ERROR = "[red on white]"


def track[T](it: Iterable[T], *, description: str, nonlinear: bool = False) -> Iterable[T]:
    total = ((len(it) ** 2) / 2 if nonlinear else len(it)) if isinstance(it, Sized) else None
    t = PROGRESS.add_task(description, total=total)
    for i, o in enumerate(it):
        yield o
        PROGRESS.advance(t, i + 1 if nonlinear else 1)
    PROGRESS.remove_task(t)
