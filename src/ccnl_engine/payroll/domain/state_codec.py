"""JSON form of a :class:`~ccnl_engine.payroll.domain.period_state.PeriodState`.

A state persisted between runs is plain JSON: every value of the state tree
is a dataclass, an enum, a ``Decimal``, a ``date``, a tuple or a scalar, each
written with a tag that names its type.  The envelope carries the schema
version and the engine and knowledge-bundle versions that wrote it: reading
accepts only the current three, because balances computed under other code
or rules cannot continue a chain reproducibly.  Types are named by
:data:`STATE_TYPES`, an explicit registry, and rebuilt through their
constructors, so every invariant of the state is checked again.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Callable, Mapping
from datetime import date
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Any, NoReturn

from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.credit_accounts import (
    SommaEsenteAccount,
    TrattamentoAccount,
    UlterioreDetrazioneAccount,
)
from ccnl_engine.payroll.domain.employment_spells import EmploymentSpell
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.run_kind import RunKind
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.sickness import SicknessEpisode
from ccnl_engine.payroll.domain.surtax_obligations import (
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    TaxYtd,
    WithholdingShortfall,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

__all__ = ["STATE_TYPES", "period_state_from_json", "period_state_to_json"]

_FEATURE = "period_state"
_FIELD = "PeriodState.json"

#: Every type a persisted state may contain, keyed by the tag it is written
#: with.  The tag is the class name, independent of the module that defines
#: it, so moving a class does not change the persisted form.
STATE_TYPES: Mapping[str, type] = MappingProxyType({
    cls.__name__: cls
    for cls in (
        DeferredShortfall,
        EarningsYtd,
        EmploymentAccrualState,
        EmploymentObligations,
        EmploymentSpell,
        FringeYtd,
        InpsBaseYtd,
        PayrollRunId,
        PaymentId,
        PeriodState,
        RecoveryObligation,
        RecoveryPlan,
        RegimeCapAccount,
        RunKind,
        SicknessEpisode,
        SommaEsenteAccount,
        SurtaxComponent,
        SurtaxObligation,
        TaxCashState,
        TaxYtd,
        TrattamentoAccount,
        UlterioreDetrazioneAccount,
        WithholdingShortfall,
    )
})


def period_state_to_json(
    state: PeriodState, *, engine_version: str, bundle_version: str
) -> str:
    """Return ``state`` as JSON text, with the versions that wrote it.

    A state holding a type outside :data:`STATE_TYPES` is a defect of the
    registry and raises ``TypeError``.

    Returns:
        The JSON text of the state.
    """
    payload = {
        "schema_version": PeriodState.SCHEMA_VERSION,
        "engine_version": engine_version,
        "bundle_version": bundle_version,
        "state": _encode(state),
    }
    return json.dumps(payload, sort_keys=True)


def period_state_from_json(
    text: str, *, engine_version: str, bundle_version: str
) -> PeriodState:
    """Return the state written by :func:`period_state_to_json`.

    Returns:
        The state, its invariants checked by its constructors.

    Raises:
        InvalidInputError: When the text is not such JSON, its schema,
            engine or bundle version is not the current one, an object has
            not the shape of its tag, names a type outside
            :data:`STATE_TYPES`, or a constructor rejects a value.
    """
    try:
        payload = json.loads(text)
    except (TypeError, ValueError, RecursionError) as exc:
        _reject(f"not JSON: {exc}")
    if not isinstance(payload, dict):
        _reject("not a persisted state")
    _check_version(payload, "schema_version", PeriodState.SCHEMA_VERSION)
    _check_version(payload, "engine_version", engine_version)
    _check_version(payload, "bundle_version", bundle_version)
    try:
        state = _decode(payload.get("state"))
    except InvalidInputError:
        raise
    except (ArithmeticError, LookupError, TypeError, ValueError, RecursionError) as exc:
        _reject(f"a value cannot be rebuilt: {exc}")
    if not isinstance(state, PeriodState):
        _reject("the state is not a PeriodState")
    return state


def _check_version(payload: dict[str, Any], key: str, expected: object) -> None:
    found = payload.get(key)
    if found != expected:
        _reject(
            f"{key} {found!r}, expected {expected!r}: a state written by another "
            "engine, bundle or schema is recomputed or imported as opening "
            "balances, not read"
        )


_NAMES: Mapping[type, str] = MappingProxyType({
    cls: name for name, cls in STATE_TYPES.items()
})


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


def _name(cls: type) -> str:
    name = _NAMES.get(cls)
    if name is None:
        msg = f"{cls.__qualname__} is not a registered state type"
        raise TypeError(msg)
    return name


def _decode(value: object) -> Any:  # noqa: ANN401
    if isinstance(value, list):
        _reject("a list outside a tagged tuple")
    if not isinstance(value, dict):
        return value
    reader = _READERS.get(frozenset(value))
    if reader is None:
        _reject(f"an object with keys {sorted(value)!r}, not a tagged value")
    return reader(value)


def _tuple(value: dict[str, Any]) -> tuple[Any, ...]:
    items = value["$tuple"]
    if not isinstance(items, list):
        _reject("a $tuple that is not a list")
    return tuple(_decode(item) for item in items)


def _dataclass(value: dict[str, Any]) -> object:
    fields = value["fields"]
    if not isinstance(fields, dict):
        _reject("a $type whose fields are not an object")
    cls = _resolve(value["$type"], enum=False)
    return cls(**{k: _decode(v) for k, v in fields.items()})


#: Readers of each tagged shape, keyed by the exact keys of the object.
_READERS: Mapping[frozenset[str], Callable[[dict[str, Any]], object]] = (
    MappingProxyType({
        frozenset({"$decimal"}): lambda v: Decimal(_text(v["$decimal"], "$decimal")),
        frozenset({"$date"}): lambda v: date.fromisoformat(_text(v["$date"], "$date")),
        frozenset({"$tuple"}): _tuple,
        frozenset({"$enum", "value"}): lambda v: _resolve(v["$enum"], enum=True)(
            v["value"]
        ),
        frozenset({"$type", "fields"}): _dataclass,
    })
)


def _text(value: object, tag: str) -> str:
    if not isinstance(value, str):
        _reject(f"a {tag} that is not a string")
    return value


def _resolve(name: object, *, enum: bool) -> type[Any]:
    cls = STATE_TYPES.get(name) if isinstance(name, str) else None
    if cls is None or issubclass(cls, Enum) != enum:
        kind = "an enum" if enum else "a dataclass"
        _reject(f"type {name!r} is not {kind} of a persisted state")
    return cls


def _reject(reason: str) -> NoReturn:
    msg = f"cannot read the persisted state: {reason}"
    raise InvalidInputError(msg, field=_FIELD, feature=_FEATURE)
