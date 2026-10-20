"""Tagged JSON tree of engine values, shared by every JSON codec of the engine.

Every value of a tree is a dataclass, an enum, a ``Decimal``, a ``date``, a
tuple, a frozenset, a mapping or a JSON scalar, each written with a tag
that names its type:

- ``{"$type": "Employment", "fields": {...}}``: a dataclass, by the fields
  its constructor takes;
- ``{"$enum": "RunKind", "value": "regular"}``: an enum member, by value;
- ``{"$decimal": "1234.50"}`` and ``{"$date": "2026-01-28"}``: exact
  decimals as strings, dates in ISO 8601;
- ``{"$tuple": [...]}``, ``{"$set": [...]}`` and
  ``{"$map": [[key, value], ...]}``: a tuple, a frozenset (items sorted by
  their JSON, so the text is stable) and a mapping with ``int`` or ``str``
  keys, which a JSON object would turn into strings.

A tag is the class name, independent of the module that defines the class.
:func:`encode` writes a tree;
:func:`~ccnl_engine.codec.tree.serializers.read_tree` reads one back through the
constructors of a closed registry, so every invariant is checked again, and
collects one :class:`~ccnl_engine.errors.InvalidInputError` per rejected
node, each with the path of the node, e.g.
``"PeriodInput.facts.events[1].hours"``.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, NoReturn

from pydantic import BaseModel

from ccnl_engine.errors import InvalidInputError

__all__ = ["encode", "loads", "reject"]


def encode(value: object, names: Mapping[type, str] | None = None) -> object:
    """Return ``value`` as a tagged tree of JSON values.

    Args:
        value: The value to write.
        names: Tag of each type a tree may hold, for a tree read back;
            ``None`` tags every dataclass, Pydantic model and enum by its
            class name, for a tree that is only written.

    When ``names`` is given, a tree holding a type outside it is a defect
    of the registry and raises ``TypeError``.

    Returns:
        The tree, ready for ``json.dumps``.
    """
    if isinstance(value, Enum):
        return {"$enum": _name(type(value), names), "value": value.value}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        init = [f.name for f in dataclasses.fields(value) if f.init]
        return _object(value, init, names)
    if isinstance(value, BaseModel):
        return _object(value, list(type(value).model_fields), names)
    return _encode_value(value, names)


def _encode_value(value: object, names: Mapping[type, str] | None) -> object:
    if isinstance(value, Decimal):
        return {"$decimal": str(value)}
    if isinstance(value, date):
        return {"$date": value.isoformat()}
    if isinstance(value, (tuple, list)):
        return {"$tuple": [encode(item, names) for item in value]}
    if isinstance(value, frozenset):
        items = [encode(item, names) for item in value]
        return {
            "$set": sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
        }
    if isinstance(value, Mapping):
        return {
            "$map": [[encode(k, names), encode(v, names)] for k, v in value.items()]
        }
    return value


def _object(
    value: object, fields: list[str], names: Mapping[type, str] | None
) -> object:
    encoded = {name: encode(getattr(value, name), names) for name in fields}
    return {"$type": _name(type(value), names), "fields": encoded}


def _name(cls: type, names: Mapping[type, str] | None) -> str:
    if names is None:
        return cls.__name__
    name = names.get(cls)
    if name is None:
        msg = f"{cls.__qualname__} is not a registered type of the tree"
        raise TypeError(msg)
    return name


def loads(text: str, *, subject: str, feature: str) -> dict[str, Any]:
    """Return the JSON object of ``text``.

    Args:
        text: The JSON text.
        subject: What the text holds, e.g. ``"the request"``, for messages.
        feature: Feature of the rejected input.

    A text that is not JSON, or not an object, raises
    :class:`~ccnl_engine.errors.InvalidInputError`.

    Returns:
        The decoded object.
    """
    try:
        payload = json.loads(text)
    except (TypeError, ValueError, RecursionError) as exc:
        reject(subject, f"not JSON: {exc}", feature=feature)
    if not isinstance(payload, dict):
        reject(subject, "not a JSON object", feature=feature)
    return payload


def reject(subject: str, reason: str, *, feature: str) -> NoReturn:
    """Reject a whole text: its envelope, not a node of its tree.

    Raises:
        InvalidInputError: Always, with no field.
    """
    msg = f"cannot read {subject}: {reason}"
    raise InvalidInputError(msg, feature=feature)
