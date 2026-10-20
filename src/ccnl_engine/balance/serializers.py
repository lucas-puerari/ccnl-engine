"""JSON form of a :class:`~ccnl_engine.balance.models.PeriodState`.

A state persisted between runs is plain JSON: the tagged tree of
:mod:`ccnl_engine.codec.serializers`, where every value is written
with a tag that names its type.  The envelope carries the schema
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

import json
from collections.abc import Callable, Mapping
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
from ccnl_engine.codec.serializers import encode, loads, reject
from ccnl_engine.codec.tree.serializers import read_tree
from ccnl_engine.contribution.base.models import InpsBaseYtd
from ccnl_engine.employment.spell.models import EmploymentSpell
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
_SUBJECT = "the persisted state"

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

_NAMES: Mapping[type, str] = MappingProxyType({
    cls: name for name, cls in STATE_TYPES.items()
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
        "state": encode(state, _NAMES),
    }
    return json.dumps(payload, sort_keys=True)


def period_state_from_json(text: str) -> PeriodState:
    """Return the state written by :func:`period_state_to_json`.

    The state of an earlier schema is migrated to the current one first.
    The engine and bundle versions that wrote it are not compared with the
    running ones: they stay in the text, for audit.

    A text that is not such JSON, whose schema version is not an integer
    from :data:`FIRST_SCHEMA_VERSION` to the current one, or whose engine
    or bundle version is not a string raises
    :class:`~ccnl_engine.errors.InvalidInputError` with no field; so does a
    migration that rejects the tree.  The first node of the state that is
    malformed, names a type outside :data:`STATE_TYPES` or is rejected by
    its constructor raises it with its path, e.g.
    ``"PeriodState.accrual.inps_bases[0]"``, as field.

    Returns:
        The state, its invariants checked by its constructors.
    """
    payload = loads(text, subject=_SUBJECT, feature=_FEATURE)
    schema = _schema_version(payload)
    for key in ("engine_version", "bundle_version"):
        if not isinstance(payload.get(key), str):
            _reject(f"{key} {payload.get(key)!r} is not a version string")
    try:
        tree = migrate_state(payload.get("state"), schema)
    except (ArithmeticError, LookupError, TypeError, ValueError) as exc:
        _reject(f"the state cannot be migrated: {exc}")
    state, errors = read_tree(
        tree, "PeriodState", types=STATE_TYPES, subject=_SUBJECT, feature=_FEATURE
    )
    if errors:
        raise errors[0]
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


def _reject(reason: str) -> NoReturn:
    reject(_SUBJECT, reason, feature=_FEATURE)
