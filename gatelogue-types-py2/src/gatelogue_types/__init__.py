from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Self

class GD():
    def __init__(self):
        sqlite3.threadsafety = 3
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = true")

    @classmethod
    def create(cls) -> Self:
        self = cls()
        cur = self.conn.cursor()
        with open(Path(__file__).parent / "create.sql") as f:
            cur.executescript(f.read())
        return self


if __name__ == "__main__":
    GD.create()
