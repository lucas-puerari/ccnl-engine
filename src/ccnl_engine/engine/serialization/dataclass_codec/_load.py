"""Deserialisation (load) helpers for frozen dataclasses and Pydantic models."""

from __future__ import annotations

import dataclasses
import typing
from collections.abc import Mapping
from dataclasses import fields
from datetime import date as _date
from decimal import Decimal
from enum import Enum
from types import UnionType
from typing import cast, get_origin

from ccnl_engine.engine.serialization.codec import (
    _STRICT_PRIMITIVES,
    _validate_primitive,
)

#: Sentinel returned by :func:`_try_union_member` when a member rejects a raw.
_NO_MATCH: object = object()

#: Known field renames by class name.  When an old snapshot carries the
#: obsolete key, :func:`_load_dataclass` migrates it to the current name.
#: Only ``True`` (or any truthy) values are safe to migrate automatically;
#: ``False`` is rejected with ``ValueError`` because the rename changed the
#: semantic boundary of the flag, making the old ``False`` ambiguous.
_FIELD_RENAMES: dict[str, dict[str, str]] = {
    "AnnualEstimate": {"part_time_pct": "part_time_ratio"},
    "Art15Deductions": {"mortgage_pre_1993": "mortgage_pre_2022"},
    "Employee": {"part_time_pct": "part_time_ratio"},
    "Employment": {"calculation_date": "as_of"},
    "PeriodPayroll": {"part_time_pct": "part_time_ratio"},
}


def _coerce_scalar(raw: object, hint: type) -> object:
    """Coerce a JSON-native *raw* value to the type described by *hint*.

    Primitive types (``bool``, ``int``, ``str``) are delegated to
    :func:`_validate_primitive`, which raises ``TypeError`` on mismatch.

    Returns:
        The coerced value; plain scalars pass through only when type matches.
    """
    if hint is Decimal:
        return Decimal(str(raw))
    if hint is _date:
        return _date.fromisoformat(str(raw))
    if isinstance(hint, type) and issubclass(hint, Enum):
        return hint(raw)
    if hint in _STRICT_PRIMITIVES:
        return _validate_primitive(raw, hint)
    return raw


def _unwrap_annotated(hint: type) -> type:
    """Strip ``Annotated[...]`` wrappers, returning the inner type.

    Returns:
        The unwrapped type, or *hint* unchanged if it is not annotated.
    """
    if get_origin(hint) is typing.Annotated:
        hint, *_ = typing.get_args(hint)
    return hint


def _load_union_hint(hint: type, raw: object) -> object:
    """Load *raw* through a ``Union``/``Optional`` type hint.

    Returns:
        The reconstructed value for the first matching union member.
    """
    args = typing.get_args(hint)
    if type(None) in args and raw is None:
        return None
    non_none = [a for a in args if a is not type(None)]
    if len(non_none) == 1:
        return _load_by_hint(non_none[0], raw)
    return _load_union(non_none, raw)


def _load_collection_hint(hint: type, origin: type, raw: object) -> object:
    """Load *raw* through a ``list``/``tuple``/``frozenset`` type hint.

    Returns:
        The reconstructed collection with every element loaded via
        :func:`_load_by_hint`.

    Raises:
        TypeError: When *raw* is a non-iterable JSON scalar (``str``, ``bytes``
            or ``dict``) that would be iterated as characters or key-value pairs
            instead of as a proper sequence element.
    """
    if isinstance(raw, (str, bytes, dict)):
        msg = f"expected a sequence, got {type(raw).__name__!r}"
        raise TypeError(msg)
    raw_seq = cast("list[object]", raw)
    if origin is frozenset:
        args = typing.get_args(hint)
        elem_hint = args[0] if args else str
        return frozenset(_load_by_hint(elem_hint, item) for item in raw_seq)
    args = typing.get_args(hint)
    elem_hint = args[0]
    items = [_load_by_hint(elem_hint, item) for item in raw_seq]
    if origin is tuple:
        return tuple(items)
    return items


def _load_by_hint(hint: type, raw: object) -> object:
    """Reconstruct an object from a JSON-native *raw* guided by *hint*.

    Returns:
        The reconstructed value for the given type hint.

    Raises:
        ValueError: When *raw* is not a member of a ``Literal`` hint.
    """
    hint = _unwrap_annotated(hint)
    origin = get_origin(hint)
    if origin is typing.Union or origin is UnionType:
        return _load_union_hint(hint, raw)
    if origin is typing.Literal:
        allowed = typing.get_args(hint)
        if raw not in allowed:
            msg = f"expected one of {allowed!r}, got {raw!r}"
            raise ValueError(msg)
        return raw
    if origin is not None:
        return _load_collection_hint(hint, origin, raw)
    if dataclasses.is_dataclass(hint):
        return _load_dataclass(hint, raw)
    if isinstance(hint, type) and hasattr(hint, "model_validate"):
        return _load_dataclass(hint, raw)
    return _coerce_scalar(raw, hint)


def _try_union_member(hint: type, raw: object) -> object:
    """Try to load *raw* as *hint*, reporting failure without exceptions.

    Returns:
        The reconstructed value, or :data:`_NO_MATCH` when *hint* rejects the
        input payload.
    """
    if dataclasses.is_dataclass(hint):
        try:
            return _load_dataclass(hint, raw)
        except (TypeError, ValueError):
            return _NO_MATCH
    if isinstance(hint, type) and hasattr(hint, "model_validate"):
        try:
            return _load_dataclass(hint, raw)
        except Exception:  # noqa: BLE001
            return _NO_MATCH
    return _NO_MATCH


def _load_union(member_hints: list[type], raw: object) -> object:
    """Reconstruct a union value from *raw*.

    Dataclass members are matched by the ``$type`` tag recorded by
    :func:`_dump` when present, falling back to trial-loading. Pydantic
    members use their discriminator field via ``model_validate``.

    Returns:
        The first member that successfully loads *raw*.

    Raises:
        ValueError: If no union member accepts the input payload.
    """
    if isinstance(raw, Mapping):
        tag = raw.get("$type")
        if isinstance(tag, str):
            for hint in member_hints:
                if dataclasses.is_dataclass(hint) and hint.__name__ == tag:
                    return _load_dataclass(hint, raw)
    for hint in member_hints:
        loaded = _try_union_member(hint, raw)
        if loaded is not _NO_MATCH:
            return loaded
    msg = f"No union member matched the input payload for {member_hints!r}."
    raise ValueError(msg)


def _apply_renames(dc_name: str, raw: Mapping[str, object]) -> Mapping[str, object]:
    """Apply :data:`_FIELD_RENAMES` migrations for *dc_name* in-place on a copy.

    Only truthy values are migrated automatically.  A falsy old value raises
    ``ValueError`` because the rename changed the flag's semantic boundary and
    the old ``False`` cannot be reliably mapped.

    Returns:
        A new dict with old keys replaced by their current equivalents.

    Raises:
        ValueError: If an old field is present with a falsy value that cannot
            be reliably migrated to the new name.
    """
    renames = _FIELD_RENAMES.get(dc_name, {})
    if not renames:
        return raw
    result = dict(raw)
    for old, new in renames.items():
        if old not in result:
            continue
        if new in result:
            del result[old]
        elif result[old]:
            result[new] = result.pop(old)
        else:
            msg = (
                f"Cannot migrate {dc_name}.{old}=False to {new}: "
                "the flag boundary changed and the old False is ambiguous. "
                "Set the current field name explicitly."
            )
            raise ValueError(msg)
    return result


def _load_pydantic_model(dc: type, raw: Mapping[str, object]) -> object:
    """Reconstruct a Pydantic model from a JSON-native dict.

    Returns:
        A new instance of *dc* built from the snapshot fields.

    Raises:
        ValueError: If an unknown field is present or a required field is
            missing from *raw*.
    """
    known = set(dc.model_fields.keys()) | {"$type"}  # type: ignore[attr-defined]
    unknown = set(raw.keys()) - known
    if unknown:
        msg = (
            f"Unknown fields {sorted(unknown)!r} in {dc.__name__} snapshot. "
            "Remove them or update the snapshot to the current schema."
        )
        raise ValueError(msg)
    for fname, finfo in dc.model_fields.items():  # type: ignore[attr-defined]
        if finfo.is_required() and fname not in raw:
            msg = f"Missing field {fname!r} in {dc.__name__} snapshot"
            raise ValueError(msg)
    clean = {k: v for k, v in raw.items() if k != "$type"}
    return dc.model_validate(clean)  # type: ignore[attr-defined]


def _load_plain_dataclass(dc: type, raw: Mapping[str, object]) -> object:
    """Reconstruct a plain frozen dataclass from a JSON-native dict.

    Returns:
        A new instance of *dc* built from the snapshot fields.

    Raises:
        ValueError: If an unknown field is present or a required field is
            missing from *raw*.
    """
    known = {f.name for f in fields(dc)} | {"$type"}
    unknown = set(raw.keys()) - known
    if unknown:
        msg = (
            f"Unknown fields {sorted(unknown)!r} in {dc.__name__} snapshot. "
            "Remove them or update the snapshot to the current schema."
        )
        raise ValueError(msg)
    hints = typing.get_type_hints(dc)
    kwargs: dict[str, object] = {}
    for f in fields(dc):
        if f.name not in raw:
            has_default = (
                f.default is not dataclasses.MISSING
                or f.default_factory is not dataclasses.MISSING
            )
            if has_default:
                continue
            msg = f"Missing field {f.name!r} in {dc.__name__} snapshot"
            raise ValueError(msg)
        kwargs[f.name] = _load_by_hint(hints[f.name], raw[f.name])
    return dc(**kwargs)


def _load_dataclass(dc: type, raw: object) -> object:
    """Reconstruct a frozen dataclass or Pydantic model from a JSON-native dict.

    Fields with defaults are skipped when absent from *raw* so that
    old serialised snapshots remain readable after new defaulted fields are
    added.  Unknown keys that do not appear in the type raise
    ``ValueError``; the special ``$type`` discriminator key is exempt.
    Known field renames (see :data:`_FIELD_RENAMES`) are migrated: only
    truthy values are safe to migrate automatically; a falsy value raises
    ``ValueError`` because the rename changed the semantic boundary of the
    flag and the old ``False`` is ambiguous.

    Returns:
        A new instance of *dc* built from the snapshot fields.

    Raises:
        TypeError: If *raw* is not a dict.
    """
    if not isinstance(raw, Mapping):
        msg = f"Expected a mapping to build {dc.__name__}, got {type(raw)!r}"
        raise TypeError(msg)
    raw = _apply_renames(dc.__name__, raw)
    if hasattr(dc, "model_fields"):
        return _load_pydantic_model(dc, raw)
    return _load_plain_dataclass(dc, raw)
