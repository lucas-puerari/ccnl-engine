"""Helpers of the codec tests: the types a value of a root type can hold."""

from __future__ import annotations

import dataclasses
import importlib
import pkgutil
import sys
import typing
from enum import Enum
from types import UnionType

import ccnl_engine as engine_package


def domain_types() -> dict[str, object]:
    """Return every class and type alias of the engine, by name.

    Returns:
        The names a forward reference of a field may resolve to.
    """
    names: dict[str, object] = {}
    for module in pkgutil.walk_packages(
        engine_package.__path__, f"{engine_package.__name__}."
    ):
        imported = importlib.import_module(module.name)
        names.update({
            k: v
            for k, v in vars(imported).items()
            if isinstance(v, (type, UnionType, typing.TypeAliasType))
        })
    return names


def _inner(hint: object, names: dict[str, object]) -> list[object]:
    if typing.get_origin(hint) is not None or isinstance(hint, UnionType):
        return list(typing.get_args(hint))
    if isinstance(hint, typing.TypeAliasType):
        return [hint.__value__]
    if isinstance(hint, type) and dataclasses.is_dataclass(hint):
        own = vars(sys.modules[hint.__module__])
        hints = typing.get_type_hints(hint, localns={**names, **own})
        return [hints[f.name] for f in dataclasses.fields(hint) if f.init]
    return []


def _is_tagged(hint: object) -> bool:
    return isinstance(hint, type) and (
        issubclass(hint, Enum) or dataclasses.is_dataclass(hint)
    )


def reachable(roots: tuple[type, ...], names: dict[str, object]) -> set[type]:
    """Return every dataclass and enum a value of ``roots`` can hold.

    Returns:
        The roots and every type reachable through the fields their
        constructors take.
    """
    found: set[type] = set()
    seen: set[int] = set()
    # Hints built on the fly are freed once popped; keeping each one alive
    # stops a later hint from reusing its id and being skipped.
    visited: list[object] = []
    pending: list[object] = list(roots)
    while pending:
        hint = pending.pop()
        if id(hint) in seen:
            continue
        seen.add(id(hint))
        visited.append(hint)
        if _is_tagged(hint):
            found.add(typing.cast("type", hint))
        pending.extend(_inner(hint, names))
    return found
