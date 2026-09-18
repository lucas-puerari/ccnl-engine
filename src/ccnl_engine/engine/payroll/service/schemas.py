"""JSON Schema generation for the public payroll API types."""

from __future__ import annotations

import dataclasses
import types
import typing
from datetime import date as _date
from decimal import Decimal

from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
from ccnl_engine.engine.payroll.domain.scenario import AnnualPayrollScenario

_SCALAR_MAP: dict[object, dict[str, object]] = {
    Decimal: {"type": "string"},
    _date: {"type": "string", "format": "date"},
    bool: {"type": "boolean"},
    int: {"type": "integer"},
    str: {"type": "string"},
}


def scenario_schema() -> dict[str, object]:
    """Return the JSON Schema for :class:`AnnualPayrollScenario`.

    The schema is derived from the Pydantic model definition and includes
    all nested types and discriminated-union tags.

    Returns:
        A JSON Schema dict (Draft 2020-12 compatible).
    """
    return AnnualPayrollScenario.model_json_schema()


def _hint_to_schema(hint: object) -> dict[str, object]:
    """Map a Python type hint to a JSON Schema fragment.

    Returns:
        A JSON Schema dict fragment for *hint*.
    """
    if hint in _SCALAR_MAP:
        return _SCALAR_MAP[hint]

    origin = typing.get_origin(hint)
    args = typing.get_args(hint)

    if origin in {typing.Union, types.UnionType}:
        non_none = [a for a in args if a is not type(None)]
        if type(None) in args and len(non_none) == 1:
            return {"oneOf": [_hint_to_schema(non_none[0]), {"type": "null"}]}

    if origin is typing.Literal:
        return {"enum": list(args)}

    if origin is tuple and args:
        return {"type": "array", "items": _hint_to_schema(args[0])}

    if origin is frozenset:
        return {"type": "array", "items": {"type": "string"}}

    return {}


def result_schema() -> dict[str, object]:
    """Return the JSON Schema for :class:`PayrollResult`.

    The schema describes the output of :func:`~ccnl_engine.compute` and
    :func:`~ccnl_engine.estimate_annual`, as produced by
    :meth:`~ccnl_engine.engine.payroll.domain.payroll_result\
.PayrollResult.to_dict`.

    Field types follow :meth:`PayrollResult.to_dict` encoding rules:
    all :class:`~decimal.Decimal` amounts are ``{"type": "string"}``,
    dates are ``{"type": "string", "format": "date"}``.

    Returns:
        A JSON Schema dict (Draft 2020-12 compatible).
    """
    hints = typing.get_type_hints(PayrollResult)
    fields_with_defaults = frozenset(
        f.name
        for f in dataclasses.fields(PayrollResult)
        if f.default is not dataclasses.MISSING
        or f.default_factory is not dataclasses.MISSING
    )
    required = sorted(
        f.name
        for f in dataclasses.fields(PayrollResult)
        if f.name not in fields_with_defaults
    )
    properties: dict[str, object] = {
        f.name: _hint_to_schema(hints[f.name])
        for f in dataclasses.fields(PayrollResult)
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "PayrollResult",
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }
