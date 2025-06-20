from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import re
    from collections.abc import Iterator


def search_all(regex: re.Pattern[str], text: str) -> Iterator[re.Match[str]]:
    pos = 0
    while (match := regex.search(text, pos)) is not None:
        pos = match.end()
        yield match


def get_stn(sts, name):
    st = next((st for st in sts if st.name.v == name), None)
    if st is None:
        msg = f"{name} not in {','.join(s.name.v for s in sts)}"
        raise ValueError(msg)
    return st
