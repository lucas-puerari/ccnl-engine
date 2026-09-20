"""Generic serialisation helpers for frozen-dataclass payroll result types.

Provides the type-agnostic primitives that are shared across all result
classes: serialisation (Python → JSON-native) and the structural helpers
used by the per-field coerce layer in the domain modules.
"""

from __future__ import annotations

import dataclasses
import types
import typing
from datetime import date as _date
from decimal import Decimal


def _unwrap_optional(raw: object, hint: type) -> tuple[object, type]:
    """If *hint* is ``X | None``, return (raw, X) — or (None, hint) when raw is None.

    Returns:
        A (raw, concrete_hint) pair with the ``None`` arm stripped.
    """
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin in {typing.Union, types.UnionType} and type(None) in args:
        if raw is None:
            return None, hint
        return raw, next(a for a in args if a is not type(None))
    return raw, hint


def _has_default(f: dataclasses.Field[object]) -> bool:
    """Return True when field *f* has a default value or factory.

    Returns:
        ``True`` when *f* has a default value or default_factory.
    """
    no_default = f.default is dataclasses.MISSING
    no_factory = f.default_factory is dataclasses.MISSING
    return not (no_default and no_factory)


def _serialise_value(value: object) -> object:  # noqa: PLR0911
    """Recursively serialise a value to a JSON-native type.

    Returns:
        A JSON-serialisable representation of *value*.
    """
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, _date):
        return value.isoformat()
    if isinstance(value, frozenset):
        return sorted(str(v) for v in value)
    if isinstance(value, tuple):
        return [_serialise_value(v) for v in value]
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _serialise_dataclass(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _serialise_dataclass(obj: object) -> dict[str, object]:
    """Serialise a dataclass instance to a plain dict.

    Returns:
        A dict with each field serialised via :func:`_serialise_value`.
    """
    out: dict[str, object] = {}
    for f in dataclasses.fields(obj):  # type: ignore[arg-type]
        out[f.name] = _serialise_value(getattr(obj, f.name))
    return out
