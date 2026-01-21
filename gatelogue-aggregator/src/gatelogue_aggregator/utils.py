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


def format_code(s: str | None) -> str | None:
    if s is None or str(s).strip().lower() in ("", "?", "??", "-", "foobar"):
        return None
    res = ""
    hyphen1 = False
    hyphen2 = False
    for match in search_all(re.compile(r"\d+|[A-Za-z]+|[^\dA-Za-z]+"), str(s).strip()):
        t = match.group(0)
        if len(t) == 0:
            continue
        if (
            (hyphen1 and t[0].isdigit())
            or (hyphen2 and t[0].isalpha())
            or (len(res) != 0 and t[0].isdigit() and res[-1].isdigit())
        ):
            res += "-"
        if hyphen1:
            hyphen1 = False
        if hyphen2:
            hyphen2 = False
        if t.isdigit():
            res += t.lstrip("0") or "0"
        elif t.isalpha():
            res += t.upper()
        elif (t == "-" and len(res) == 0) or (len(res) != 0 and res[-1].isdigit()):
            hyphen1 = True
        elif len(res) != 0 and res[-1].isalpha():
            hyphen2 = True

    return res


def format_air_airport_code[T: (str, None)](s: T) -> T:
    if s is None:
        return None
    s = str(s).upper()
    s = AIRPORT_ALIASES.get(s.strip(), s)
    if len(s) == 4 and s[3] == "T":
        return s[:3]
    return s
