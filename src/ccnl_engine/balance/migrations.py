"""Steps that bring a persisted state of an earlier schema to the current one.

Each bump of :attr:`~ccnl_engine.balance.models.PeriodState.SCHEMA_VERSION`
comes with the step from the previous version, so a stored state stays
readable (a test holds every version from the first).
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

__all__ = [
    "FIRST_SCHEMA_VERSION",
    "STATE_MIGRATIONS",
    "StateMigration",
    "tfr_quotas_unknown",
]

#: A step of the state tree (the ``state`` value of the JSON) from one schema
#: version to the next.
type StateMigration = Callable[[object], object]

#: The oldest schema a persisted state is still read from: the first one
#: written, states of earlier engines were not persisted.
FIRST_SCHEMA_VERSION = 14


def tfr_quotas_unknown(tree: object) -> object:
    """Return a state tree of schema 14 as schema 15 reads it.

    Schema 15 counts the TFR the runs accrue per competence year
    (``EmploymentAccrualState.tfr_quotas``).  A state of schema 14 counted
    none: the quotas of the years it closed runs of are not known, so they
    are known from the year after the last of them.

    Returns:
        A copy of ``tree`` whose accrual state knows the quotas from the
        year after its last closed run, or of every year without one.
    """
    migrated: Any = copy.deepcopy(tree)
    accrual = migrated["fields"]["accrual"]["fields"]
    runs = accrual["competence_runs"]["$tuple"]
    years = [run["fields"]["year"] for run in runs]
    accrual["tfr_quotas_known_from"] = max(years) + 1 if years else None
    return migrated


def _leave_unknown(tree: object) -> object:
    """Add the leave account to a schema 15 state: unknown, no balance.

    Schema 16 carries the leave balances in the competence state.  A state
    of schema 15 was written before the engine accrued leave, so the leave
    of its employment is not known: the run that closes the employment pays
    no residual and blocks, as for balances imported without it.

    Returns:
        The state tree of schema 16.

    Raises:
        TypeError: When the tree has not the shape of a persisted state.
    """
    if not isinstance(tree, dict):
        msg = "a persisted state is a tagged PeriodState"
        raise TypeError(msg)
    accrual = tree["fields"]["accrual"]["fields"]
    leave = {
        "$type": "LeaveAccount",
        "fields": {"balances": {"$tuple": []}, "known": False},
    }
    fields = {**tree["fields"]}
    fields["accrual"] = {
        **tree["fields"]["accrual"],
        "fields": {**accrual, "leave": leave},
    }
    return {**tree, "fields": fields}


def _no_personal_withholdings(tree: object) -> object:
    """Add the personal withholdings of schema 17 to a schema 16 state: none.

    Returns:
        A copy of ``tree`` whose obligations hold no amount withheld to date.
    """
    migrated: Any = copy.deepcopy(tree)
    obligations = migrated["fields"]["cash"]["fields"]["obligations"]
    obligations["fields"]["personal_withholdings"] = {"$tuple": []}
    return migrated


def _no_form730(tree: object) -> object:
    """Add the 730 installments of schema 18 to a schema 17 state: none.

    Returns:
        A copy of ``tree`` whose obligations carry no 730 installment.
    """
    migrated: Any = copy.deepcopy(tree)
    obligations = migrated["fields"]["cash"]["fields"]["obligations"]
    obligations["fields"]["form730"] = {"$tuple": []}
    return migrated


#: The step from each schema version to the next, keyed by the version it reads.
#: A bump of :attr:`PeriodState.SCHEMA_VERSION` comes with the step from the previous
#: one, so a stored state stays readable (a test holds every version from the first).
STATE_MIGRATIONS: Mapping[int, StateMigration] = MappingProxyType({
    14: tfr_quotas_unknown,
    15: _leave_unknown,
    16: _no_personal_withholdings,
    17: _no_form730,
})
