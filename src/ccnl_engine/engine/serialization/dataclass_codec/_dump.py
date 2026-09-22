"""Serialisation (dump) helpers for frozen dataclasses and Pydantic models."""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from datetime import date as _date
from decimal import Decimal
from enum import Enum

from ccnl_engine.engine.primitives import FrozenDict


def _dump_frozenset(value: frozenset[object]) -> list[str]:
    """Serialise a frozenset to a sorted list of strings.

    Returns:
        A sorted list of the string representations of *value*'s members.
    """
    return sorted(str(v) for v in value)


def _dump_dataclass(value: object) -> dict[str, object]:
    """Serialise a dataclass to a ``$type``-tagged dict.

    Returns:
        A dict with ``$type`` set to the class name, plus every field.
    """
    out: dict[str, object] = {"$type": type(value).__name__}
    out.update({
        f.name: _dump(getattr(value, f.name))
        for f in dataclasses.fields(value)  # type: ignore[arg-type]
    })
    return out


def _dump_dict(value: dict[str, object]) -> dict[str, object]:
    """Recursively serialise a dict.

    Returns:
        A new dict with every value serialised via :func:`_dump`.
    """
    return {k: _dump(v) for k, v in value.items()}


def _dump(value: object) -> object:  # noqa: PLR0911
    """Convert an input value to a JSON-native object (lossless round-trip).

    Returns:
        A JSON-native value: ``str``/``int``/``bool``/``None`` scalars pass
        through, ``Decimal`` becomes its ``str`` form, dates become ISO
        strings, ``Enum`` members become their value, dataclasses become dicts
        tagged with a ``$type`` marker, pydantic models are dumped first.

    Raises:
        TypeError: If *value* is not JSON-serialisable by any of the above.
    """
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, _date):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, frozenset):
        return _dump_frozenset(value)
    if isinstance(value, (list, tuple)):
        return [_dump(v) for v in value]
    if dataclasses.is_dataclass(value):
        return _dump_dataclass(value)
    if hasattr(value, "model_dump"):
        return _dump(value.model_dump())
    if isinstance(value, dict):
        return _dump_dict(value)
    msg = f"Cannot serialise input value of type {type(value)!r}"
    raise TypeError(msg)


def _deep_freeze(value: object) -> object:
    """Recursively convert dicts to FrozenDict and lists to tuples.

    The result is deeply immutable: nested dicts and lists are converted
    at every level so that no element can be mutated after construction.
    Unlike ``MappingProxyType``, ``FrozenDict`` supports ``copy.deepcopy``
    and pickle without errors.

    Returns:
        A recursively frozen copy of *value*.
    """
    if isinstance(value, Mapping):
        return FrozenDict({k: _deep_freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_deep_freeze(v) for v in value)
    return value


def _deep_thaw(value: object) -> object:
    """Recursively convert FrozenDict to dict and tuples to lists.

    Reverses :func:`_deep_freeze` to produce a plain JSON-native structure.

    Returns:
        A plain dict/list copy of *value*.
    """
    if isinstance(value, FrozenDict):
        return {k: _deep_thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_deep_thaw(v) for v in value]
    return value
