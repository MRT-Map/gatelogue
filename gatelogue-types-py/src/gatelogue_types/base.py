from __future__ import annotations

import re
import warnings
from typing import TYPE_CHECKING, LiteralString, Literal

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from gatelogue_types.node import Node


def _format_str[T: str](s: T | None) -> T | None:
    if s is None or s.strip().lower() in ("", "?", "??", "-"):
        return None
    return s.strip()


def _format_code[T: str](s: T | None) -> T | None:
    def search_all(regex: re.Pattern[str], text: str) -> Iterator[re.Match[str]]:
        pos = 0
        while (m := regex.search(text, pos)) is not None:
            pos = m.end()
            yield m

    if (s := _format_str(s)) is None:
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

def _warn_clash(warn_fn: Callable[[str], object], column: str, table: str, str_instance1: str, self_v, str_instance2: str, other_v, self_sources: set[int], other_sources: set[int], priority: Literal["former", "latter"]):
    warn_fn(
        f"{column} in table {table} is different "
        f"between {str_instance1} ({self_v}) and {str_instance2} ({other_v}). " +
        (f"Former has higher priority of {self_sources} than latter which has {other_sources}" if priority == "former" else f"Latter has higher priority of {other_sources} than former which has {self_sources}")
    )

class _Column[T]:
    def __init__(
        self,
        name: LiteralString,
        table: LiteralString,
        sourced: bool = False,
        formatter: Callable[[T], T] | None = None,
    ):
        self.name = f'"{name}"'
        self.table = table
        self.sourced = sourced
        self.formatter = formatter

    def __get__(self, instance: Node, owner: type[Node]) -> T:
        return instance.conn.execute(
            f"SELECT {self.name} FROM {self.table} WHERE i = :i", dict(i=instance.i)
        ).fetchone()[0]

    def __set__(self, instance: Node, value: T | tuple[set[int], T]):
        srcs, value = value if isinstance(value, tuple) else (instance.sources, value)
        if self.formatter is not None:
            value = self.formatter(value)
        cur = instance.conn.cursor()
        if self.sourced:
            old_value = self.__get__(instance, type(instance))
        else:
            old_value = None
        cur.execute(f"UPDATE {self.table} SET {self.name} = :value WHERE i = :i", dict(value=value, i=instance.i))
        if not self.sourced:
            return
        if value != old_value:
            cur.execute(f"UPDATE {self.table + 'Source'} SET {self.name} = false WHERE i = :i", dict(i=instance.i))
        for src in srcs:
            cur.execute(
                f"INSERT INTO {self.table + 'Source'} (i, source, {self.name}) VALUES (:i, :source, :bool) "
                f"ON CONFLICT (i, source) DO UPDATE SET {self.name} = :bool",
                dict(bool=value is not None, i=instance.i, source=src),
            )

    def sources(self, instance: Node) -> set[int]:
        return {
            src
            for (src,) in instance.conn.execute(
                f"SELECT DISTINCT source FROM {self.table + 'Source'} WHERE i = :i AND {self.name} = true",
                dict(i=instance.i),
            ).fetchall()
        }

    def _merge(self, instance1: Node, instance2: Node, str_instance1: str | None = None, str_instance2: str | None = None, warn_fn: Callable[[str], object] = warnings.warn):
        str_instance1 = str_instance1 or str(instance1)
        str_instance2 = str_instance2 or str(instance2)
        self_v = self.__get__(instance1, type(instance1))
        other_v = self.__get__(instance2, type(instance2))
        if not self.sourced:
            if self_v != other_v:
                self_sources = instance1.sources
                other_sources = instance2.sources
                if min(self_sources) < min(other_sources):
                    if self_sources != other_sources:
                        _warn_clash(warn_fn, "Column " + self.name, self.table, str_instance1, self_v, str_instance2, other_v, self_sources, other_sources, "former")
                else:
                    if self_sources != other_sources:
                        _warn_clash(warn_fn, "Column " + self.name, self.table, str_instance1, self_v, str_instance2, other_v, self_sources, other_sources, "latter")
                    self.__set__(instance1, (self_sources, other_v))
            return
        match (self_v, other_v):
            case (None, None):
                pass
            case (_, None):
                pass
            case (None, _):
                sources = self.sources(instance2)
                self.__set__(instance1, (sources, other_v))
            case (_, _) if self_v != other_v:
                self_sources = self.sources(instance1)
                other_sources = self.sources(instance2)
                if min(self_sources) < min(other_sources):
                    if self_sources != other_sources:
                        _warn_clash(warn_fn, "Column " + self.name, self.table, str_instance1, self_v, str_instance2, other_v, self_sources, other_sources, "former")
                    self.__set__(instance2, None)
                else:
                    if self_sources != other_sources:
                        _warn_clash(warn_fn, "Column " + self.name, self.table, str_instance1, self_v, str_instance2, other_v, self_sources, other_sources, "latter")
                    self.__set__(instance1, (other_sources, other_v))


class _CoordinatesColumn:
    name = "coordinates"

    def __get__(self, instance: Node, owner: type[Node]) -> tuple[int, int] | None:
        x, y = instance.conn.execute("SELECT x, y from NodeLocation WHERE i = :i", dict(i=instance.i)).fetchone()
        return None if x is None or y is None else (x, y)

    def __set__(self, instance: Node, value: tuple[int, int] | None | tuple[set[int], tuple[int, int] | None]):
        srcs, value = value if value is not None and isinstance(value[0], set) else (instance.sources, value)
        x, y = (None, None) if value is None else value
        cur = instance.conn.cursor()
        old_value = self.__get__(instance, type(instance))
        cur.execute("UPDATE NodeLocation SET x = :x, y = :y WHERE i = :i", dict(x=x, y=y, i=instance.i))

        if value != old_value:
            cur.execute("UPDATE NodeLocationSource SET coordinates = false WHERE i = :i", dict(i=instance.i))
        for src in srcs:
            cur.execute(
                "INSERT INTO NodeLocationSource (i, source, coordinates) VALUES (:i, :source, :bool) "
                "ON CONFLICT (i, source) DO UPDATE SET coordinates = :bool",
                dict(bool=value is not None, i=instance.i, source=src),
            )

    @staticmethod
    def sources(instance: Node) -> set[int]:
        return {
            src
            for (src,) in instance.conn.execute(
                "SELECT DISTINCT source FROM NodeLocationSource WHERE i = :i AND coordinates = true", dict(i=instance.i)
            ).fetchall()
        }

    def _merge(self, instance1: Node, instance2: Node, str_instance1: str | None = None, str_instance2: str | None = None, warn_fn: Callable[[str], object] = warnings.warn):
        str_instance1 = str_instance1 or str(instance1)
        str_instance2 = str_instance2 or str(instance2)
        self_v = self.__get__(instance1, type(instance1))
        other_v = self.__get__(instance2, type(instance2))
        match (self_v, other_v):
            case (None, None):
                pass
            case (_, None):
                pass
            case (None, _):
                sources = self.sources(instance2)
                self.__set__(instance1, (sources, other_v))
            case (_, _) if self_v != other_v:
                self_sources = self.sources(instance1)
                other_sources = self.sources(instance2)
                if min(self_sources) < min(other_sources):
                    if self_sources != other_sources:
                        _warn_clash(warn_fn, "Columns x/y", "NodeLocation", str_instance1, self_v, str_instance2, other_v, self_sources, other_sources, "former")
                    self.__set__(instance2, None)
                else:
                    if self_sources != other_sources:
                        _warn_clash(warn_fn, "Columns x/y", "NodeLocation", str_instance1, self_v, str_instance2, other_v, self_sources, other_sources, "latter")
                    self.__set__(instance1, (other_sources, other_v))


class _FKColumn[T: Node | None]:
    def __init__(self, ty: type[T], name: LiteralString, table: LiteralString, sourced: bool = False):
        self.name = name
        self.table = table
        self.sourced = sourced
        self.ty = ty

    def __get__(self, instance: Node, owner: type[Node]) -> T:
        target_i = _Column(self.name, self.table, self.sourced).__get__(instance, owner)
        if target_i is None:
            return None
        return self.ty(instance.conn, target_i)

    def __set__(self, instance: Node, value: T | tuple[int, T]):
        _Column(self.name, self.table, self.sourced).__set__(instance, None if value is None else value.i)

    def _merge(self, instance1: Node, instance2: Node, str_instance1: str | None = None, str_instance2: str | None = None, warn_fn: Callable[[str], object] = warnings.warn):
        _Column(self.name, self.table, self.sourced)._merge(instance1, instance2, str_instance1, str_instance2, warn_fn)


class _SetAttr[T]:
    def __init__(
        self,
        table: LiteralString,
        table_column: LiteralString,
        sourced: bool = False,
        formatter: Callable[[T], T] | None = None,
    ):
        self.table = table
        self.table_column = table_column
        self.sourced = sourced
        self.formatter = formatter

    def __get__(self, instance: Node, owner: type[Node]) -> set[T]:
        return {
            v
            for (v,) in instance.conn.execute(
                f"SELECT {self.table_column} FROM {self.table} WHERE i = :i", dict(i=instance.i)
            ).fetchall()
        }

    def __set__(self, instance: Node, values: set[T] | tuple[set[int], set[T]]):
        srcs, values = values if isinstance(values, tuple) else (instance.sources, values)
        if self.formatter is not None:
            values = {self.formatter(value) for value in values}
        source_params = "?, " * (len(srcs) - 1) + "?"

        cur = instance.conn.cursor()
        if not self.sourced:
            cur.execute(f"DELETE FROM {self.table} WHERE i = :i", dict(i=instance.i))
            cur.executemany(
                f"INSERT INTO {self.table} (i, {self.table_column}) VALUES (:i, :value)",
                [dict(i=instance.i, value=value) for value in values],
            )
            return
        existing_values = {
            v
            for (v,) in cur.execute(
                f"SELECT {self.table_column} FROM {self.table + 'Source'} WHERE i = ? AND source IN ({source_params})",
                (instance.i, *srcs),
            ).fetchall()
        }
        for new_value in values - existing_values:
            cur.execute(
                f"INSERT INTO {self.table} (i, {self.table_column}) VALUES (:i, :value) "
                f"ON CONFLICT (i, {self.table_column}) DO NOTHING",
                dict(i=instance.i, value=new_value),
            )
            cur.executemany(
                f"INSERT INTO {self.table + 'Source'} (i, {self.table_column}, source) VALUES (:i, :value, :source) "
                f"ON CONFLICT (i, {self.table_column}, source) DO NOTHING",
                [dict(i=instance.i, value=new_value, source=src) for src in srcs],
            )
        for old_value in existing_values - values:
            cur.execute(
                f"DELETE FROM {self.table + 'Source'} WHERE i = ? AND {self.table_column} = ? AND source IN ({source_params})",
                (instance.i, old_value, *srcs),
            )
            if (
                cur.execute(
                    f"SELECT count(i) FROM {self.table + 'Source'} WHERE i = :i AND {self.table_column} = :value",
                    dict(i=instance.i, value=old_value),
                ).fetchone()[0]
                == 0
            ):
                cur.execute(
                    f"DELETE FROM {self.table} WHERE i = :i AND {self.table_column} = :value",
                    dict(i=instance.i, value=old_value),
                )

    def _merge(self, instance1: Node, instance2: Node, *_, **__):
        cur = instance1.conn.cursor()
        cur.execute(
            f"INSERT INTO {self.table} (i, {self.table_column}) "
            f"SELECT :i1, {self.table_column} FROM {self.table} WHERE i = :i2 "
            f"ON CONFLICT (i, {self.table_column}) DO NOTHING",
            dict(i1=instance1.i, i2=instance2.i),
        )
        if self.sourced:
            cur.execute(
                f"UPDATE OR REPLACE {self.table + 'Source'} SET i = :i1 WHERE i = :i2",
                dict(i1=instance1.i, i2=instance2.i),
            )
        cur.execute(f"DELETE FROM {self.table} WHERE i = :i2", dict(i1=instance1.i, i2=instance2.i))
