from __future__ import annotations

import rich.progress

PROGRESS: rich.progress.Progress = rich.progress.Progress(transient=True)
PROGRESS.start()

INFO1 = "[yellow]"
INFO2 = "[green]  "
INFO3 = "[dim green]    "
RESULT = "[cyan]  "
ERROR = "[red on white]"
