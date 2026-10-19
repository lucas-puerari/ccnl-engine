"""JSON form of a :class:`~ccnl_engine.balance.models.PeriodState`.

A state persisted between runs is plain JSON: every value of the state tree
is a dataclass, an enum, a ``Decimal``, a ``date``, a tuple or a scalar, each
written with a tag that names its type.  The envelope carries the schema
version and the engine and knowledge-bundle versions that wrote it.  Reading
checks only the schema: a state of an earlier schema, back to
:data:`FIRST_SCHEMA_VERSION`, is brought to the current one by the
:data:`STATE_MIGRATIONS` before it is decoded, and the engine and bundle
versions stay in the text for audit, so a release of either does not
invalidate the stored states.  Types are named by :data:`STATE_TYPES`, an
explicit registry, and rebuilt through their constructors, so every
invariant of the state is checked again.
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

from ccnl_engine.balance.cash.account.models import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    TaxYtd,
    WithholdingShortfall,
)
from ccnl_engine.balance.cash.models import TaxCashState
from ccnl_engine.balance.competence.models import EmploymentAccrualState
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.balance.obligation.models import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.calendar.payment.models import PaymentId
from ccnl_engine.contribution.base.models import InpsBaseYtd
from ccnl_engine.employment.spell.models import EmploymentSpell
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.run.models import PayrollRunId
from ccnl_engine.run.types import RunKind
from ccnl_engine.sickness.models import SicknessEpisode
from ccnl_engine.surtax.obligation.models import (
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.tax_credit.account.models import (
    SommaEsenteAccount,
    TrattamentoAccount,
    UlterioreDetrazioneAccount,
)
from ccnl_engine.tax_credit.recovery.models import RecoveryPlan
from ccnl_engine.withholding.deferral.inputs import DeferredShortfall

__all__ = [
    "FIRST_SCHEMA_VERSION",
    "STATE_MIGRATIONS",
    "STATE_TYPES",
    "StateMigration",
    "migrate_state",
    "period_state_from_json",
    "period_state_to_json",
]

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


#: A step of the state tree (the ``state`` value of the JSON) from one schema
#: version to the next.
type StateMigration = Callable[[object], object]

#: The oldest schema a persisted state is still read from: the first one
#: written, states of earlier engines were not persisted.
FIRST_SCHEMA_VERSION = 14

#: The step from each schema version to the next, keyed by the version it
#: reads.  A bump of :attr:`PeriodState.SCHEMA_VERSION` comes with the step
#: from the previous version, so a stored state stays readable; a test holds
#: the registry to every version from :data:`FIRST_SCHEMA_VERSION`.
STATE_MIGRATIONS: Mapping[int, StateMigration] = MappingProxyType({})


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


def period_state_from_json(text: str) -> PeriodState:
    """Return the state written by :func:`period_state_to_json`.

    The state of an earlier schema is migrated to the current one first.
    The engine and bundle versions that wrote it are not compared with the
    running ones: they stay in the text, for audit.

    Returns:
        The state, its invariants checked by its constructors.

    Raises:
        InvalidInputError: When the text is not such JSON, its schema
            version is not an integer from :data:`FIRST_SCHEMA_VERSION` to
            the current one, its engine or bundle version is not a string,
            an object has not the shape of its tag, names a type outside
            :data:`STATE_TYPES`, or a migration or a constructor rejects a
            value.
    """
    try:
        payload = json.loads(text)
    except (TypeError, ValueError, RecursionError) as exc:
        _reject(f"not JSON: {exc}")
    if not isinstance(payload, dict):
        _reject("not a persisted state")
    schema = _schema_version(payload)
    for key in ("engine_version", "bundle_version"):
        if not isinstance(payload.get(key), str):
            _reject(f"{key} {payload.get(key)!r} is not a version string")
    try:
        tree = migrate_state(payload.get("state"), schema)
        state = _decode(tree)
    except InvalidInputError:
        raise
    except (ArithmeticError, LookupError, TypeError, ValueError, RecursionError) as exc:
        _reject(f"a value cannot be rebuilt: {exc}")
    if not isinstance(state, PeriodState):
        _reject("the state is not a PeriodState")
    return state


def migrate_state(
    tree: object,
    version: int,
    *,
    migrations: Mapping[int, StateMigration] = STATE_MIGRATIONS,
    target: int = PeriodState.SCHEMA_VERSION,
) -> object:
    """Return the state tree of schema ``version`` brought to ``target``.

    Each step of ``migrations`` from ``version`` up to ``target`` is applied
    in order; a tree already of ``target`` is returned as it is.  A step
    missing from ``migrations`` is a defect of the registry and raises
    ``KeyError``.

    Returns:
        The state tree of schema ``target``.
    """
    for step in range(version, target):
        tree = migrations[step](tree)
    return tree


def _schema_version(payload: dict[str, Any]) -> int:
    found = payload.get("schema_version")
    if type(found) is not int:
        _reject(f"schema_version {found!r} is not an integer")
    if found > PeriodState.SCHEMA_VERSION:
        _reject(
            f"schema_version {found}, newer than {PeriodState.SCHEMA_VERSION}: "
            "a state written by a later engine is read by that engine"
        )
    if found < FIRST_SCHEMA_VERSION:
        _reject(
            f"schema_version {found}, older than {FIRST_SCHEMA_VERSION}: the "
            "state is recomputed or imported as opening balances, not read"
        )
    return found


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
