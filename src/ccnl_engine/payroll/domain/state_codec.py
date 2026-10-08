"""JSON form of a :class:`~ccnl_engine.payroll.domain.period_state.PeriodState`.

A state persisted between runs is plain JSON: every value of the state tree
is a dataclass, an enum, a ``Decimal``, a ``date``, a tuple or a scalar, each
written with a tag that names its type.  Reading checks the schema version
and rebuilds only types of the payroll domain package, through their
constructors, so every invariant of the state is checked again.
"""

from __future__ import annotations

import dataclasses
import importlib
import json
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, NoReturn

from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["period_state_from_json", "period_state_to_json"]

_FEATURE = "period_state"
_FIELD = "PeriodState.json"
#: The only package whose types a persisted state may name.
_PACKAGE = "ccnl_engine.payroll.domain."


def period_state_to_json(state: PeriodState) -> str:
    """Return ``state`` as JSON text, with its schema version.

    Returns:
        The JSON text of the state.
    """
    payload = {"schema_version": PeriodState.SCHEMA_VERSION, "state": _encode(state)}
    return json.dumps(payload, sort_keys=True)


def period_state_from_json(text: str) -> PeriodState:
    """Return the state written by :func:`period_state_to_json`.

    A text that is not such JSON, whose schema version is not the current
    one, or that names a type outside the payroll domain raises
    :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.

    Returns:
        The state, its invariants checked by its constructors.
    """
    try:
        payload = json.loads(text)
    except (TypeError, ValueError) as exc:
        _reject(f"not JSON: {exc}")
    if not isinstance(payload, dict):
        _reject("not a persisted state")
    version = payload.get("schema_version")
    if version != PeriodState.SCHEMA_VERSION:
        _reject(
            f"schema version {version!r}, expected {PeriodState.SCHEMA_VERSION}: "
            "a state of another version is recomputed or imported, not read"
        )
    state = _decode(payload.get("state"))
    if not isinstance(state, PeriodState):
        _reject("the state is not a PeriodState")
    return state


def _encode(value: object) -> object:
    if isinstance(value, Enum):
        return {"$enum": _name(type(value)), "value": value.value}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        fields = {
            f.name: _encode(getattr(value, f.name))
            for f in dataclasses.fields(value)
            if f.init
        }
        return {"$type": _name(type(value)), "fields": fields}
    if isinstance(value, Decimal):
        return {"$decimal": str(value)}
    if isinstance(value, date):
        return {"$date": value.isoformat()}
    if isinstance(value, (tuple, frozenset)):
        return {"$tuple": [_encode(item) for item in value]}
    return value


#: Readers of the tagged scalars and tuples.
_TAGGED: dict[str, Callable[[Any], object]] = {
    "$decimal": Decimal,
    "$date": date.fromisoformat,
    "$tuple": lambda items: tuple(_decode(item) for item in items),
}


def _decode(value: object) -> Any:  # noqa: ANN401
    if isinstance(value, list):
        _reject("a list outside a tagged tuple")
    if not isinstance(value, dict):
        return value
    tag = next((t for t in _TAGGED if t in value), None)
    if tag is not None:
        return _TAGGED[tag](value[tag])
    if "$enum" in value:
        return _resolve(value["$enum"], Enum)(value["value"])
    if "$type" not in value:
        _reject("an untagged object")
    cls = _resolve(value["$type"], None)
    return cls(**{k: _decode(v) for k, v in value["fields"].items()})


def _name(cls: type) -> str:
    return f"{cls.__module__}.{cls.__qualname__}"


def _resolve(name: object, base: type | None) -> type[Any]:
    if not isinstance(name, str) or not name.startswith(_PACKAGE):
        _reject(f"type {name!r} is outside the payroll domain")
    module, _, attr = name.rpartition(".")
    cls = getattr(importlib.import_module(module), attr, None)
    wanted = dataclasses.is_dataclass if base is None else _subclass(base)
    if not isinstance(cls, type) or not wanted(cls):
        _reject(f"type {name!r} is not a state type")
    return cls


def _subclass(base: type) -> Any:  # noqa: ANN401
    return lambda cls: issubclass(cls, base)


def _reject(reason: str) -> NoReturn:
    msg = f"cannot read the persisted state: {reason}"
    raise InvalidInputError(msg, field=_FIELD, feature=_FEATURE)
