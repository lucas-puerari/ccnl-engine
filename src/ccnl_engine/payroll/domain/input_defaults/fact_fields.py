"""Defaults of the fact types of :mod:`ccnl_engine.inputs`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.input_defaults.model import (
    FactEnforcement,
    absence_is_fact,
    requires_fact,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.domain.input_defaults.model import FieldDefault

__all__ = ["FACT_DEFAULTS"]

_REPORTED = FactEnforcement.REPORTED
_PENDING = FactEnforcement.PENDING


def _dependent(fact: str, reason: str) -> FieldDefault:
    return requires_fact("family_deductions", f"dependent.{fact}", _PENDING, reason)


#: Accounts of imported balances: zero is an account without movement.
_ACCOUNTS = (
    "gross",
    "taxable",
    "inps_employee",
    "pension_deducted",
    "irpef_withheld",
    "surtax_withheld",
    "municipal_advance_withheld",
    "regional_settled",
    "municipal_settled",
    "fringe_value",
    "fringe_taxed",
    "pdr",
    "trattamento_recognized",
    "trattamento_recovered",
    "somma_esente_recognized",
    "somma_esente_recovered",
    "ulteriore_recognized",
    "ulteriore_recovered",
    "irpef_shortfall",
    "surtax_shortfall",
    "credit_recovery_shortfall",
    "work_time_regime_used",
)
#: Annual amounts last computed by the previous provider, and their reasons.
_LAST_COMPUTED = tuple(
    f"{credit}_{suffix}"
    for credit in ("trattamento", "somma_esente", "ulteriore")
    for suffix in ("due", "reason")
)
_ACCOUNT = absence_is_fact(
    "an imported account left out had no movement: the previous provider "
    "states every account it kept"
)
_NOT_COMPUTED = absence_is_fact(
    "the previous provider did not compute the annual amount: the engine "
    "computes it from the imported totals"
)
_IMPORTED_LIST = absence_is_fact(
    "nothing of that kind happened earlier in the tax year"
)


def _carried(capability: str, fact: str, what: str) -> FieldDefault:
    return requires_fact(
        capability,
        f"opening_balances.{fact}",
        _PENDING,
        f"no {what} carried from an earlier run: what the previous provider "
        "determined is never withheld unless imported",
    )


#: Classification of each defaulted field of the fact types.
FACT_DEFAULTS: Mapping[str, FieldDefault] = {
    "Apprentice.track": requires_fact(
        "base_salary",
        "employment.contract_type.track",
        _REPORTED,
        "the unique track of the level; several tracks raise an input error",
    ),
    "ContributionHistory.contributory_option": absence_is_fact(
        "the option for the contributory system is an act of the worker "
        "(L. 335/1995 art. 1 c. 23): not exercised unless stated"
    ),
    "Dependent.birth_date": requires_fact(
        "family_deductions",
        "dependent.birth_date",
        _REPORTED,
        "a child without it raises an input error; no other dependant reads it",
    ),
    "Dependent.disabled": absence_is_fact(
        "the increased deduction needs a certified disability (L. 104/1992 "
        "art. 3): not stated, it does not apply"
    ),
    "Dependent.own_income": _dependent(
        "own_income", "no own income: the dependant is within the income limit"
    ),
    "Dependent.dependent_from": _dependent(
        "dependent_from", "dependant from 1 January"
    ),
    "Dependent.dependent_until": _dependent(
        "dependent_until", "dependant until 31 December"
    ),
    "Dependent.allocation_pct": _dependent(
        "allocation_pct", "the whole deduction to this worker"
    ),
    "Dependent.cohabiting": _dependent(
        "cohabiting", "cohabiting: the ascendant deduction is granted"
    ),
    "Dependent.residency_eligibility": _dependent(
        "residency_eligibility",
        "the residency condition of art. 12 c. 2-bis TUIR is met",
    ),
    "EmploymentPeriod.ended_on": absence_is_fact("the employment has not ended"),
    "FamilyComposition.dependents": absence_is_fact(
        "a composition without dependants states that there is none"
    ),
    "FamilyComposition.sole_parent": absence_is_fact(
        "the sole-parent condition of art. 12 c. 1 lett. c TUIR is declared "
        "by the worker: not declared, it does not apply"
    ),
    "InpsBaseYtd.own": absence_is_fact(
        "no base of this employment in the competence year"
    ),
    "InpsBaseYtd.other_employers": requires_fact(
        "inps_employee",
        "opening_balances.inps_bases.other_employers",
        _PENDING,
        "no other employer: the IVS massimale and the 1% threshold count this "
        "employment only",
    ),
    "InpsBaseYtd.additional_ivs": absence_is_fact(
        "this employment withheld no additional 1% IVS in the competence year"
    ),
    "InpsBaseYtd.other_employers_additional_ivs": requires_fact(
        "inps_employee",
        "opening_balances.inps_bases.other_employers_additional_ivs",
        _REPORTED,
        "unknown 1% of the other employers: with a base of theirs, a run "
        "settling the additional 1% IVS has a missing_fact blocker",
    ),
    "InpsBaseYtd.month": absence_is_fact(
        "the next run is the first of this employment in its competence month"
    ),
    "InpsBaseYtd.month_base": absence_is_fact(
        "the next run is the first of this employment in its competence month"
    ),
    "OpeningBalances.payments": _IMPORTED_LIST,
    "OpeningBalances.competence_runs": _IMPORTED_LIST,
    "OpeningBalances.inps_bases": requires_fact(
        "inps_employee",
        "opening_balances.inps_bases",
        _PENDING,
        "no imported INPS base: the massimale and the 1% threshold restart "
        "from the payments the engine computes",
    ),
    "OpeningBalances.sickness_episodes": _IMPORTED_LIST,
    **{f"OpeningBalances.{name}": _ACCOUNT for name in _ACCOUNTS},
    **{f"OpeningBalances.{name}": _NOT_COMPUTED for name in _LAST_COMPUTED},
    "OpeningBalances.recoveries": _carried(
        "trattamento_integrativo", "recoveries", "credit recovery"
    ),
    "OpeningBalances.surtax_obligations": _carried(
        "addizionale_regionale", "surtax_obligations", "surtax"
    ),
    "OpeningBalances.deferred_shortfall": absence_is_fact(
        "no written request to defer the shortfall (art. 23 c. 3 DPR 600/1973)"
    ),
    "PeriodState.accrual": absence_is_fact(
        "a state built by the caller starts from empty accrual accounts; the "
        "opening state of a run is classified on PeriodInput"
    ),
    "PeriodState.cash": absence_is_fact(
        "a state built by the caller starts from empty tax accounts; the "
        "opening state of a run is classified on PeriodInput"
    ),
    "PriorYearTaxFacts.employment_income": requires_fact(
        "rinnovo_substitute_tax",
        "prior_year.employment_income",
        _REPORTED,
        "unknown prior-year income: a regime capped on it is undetermined, "
        "with a blocker",
    ),
    "PriorYearTaxFacts.waived_regimes": absence_is_fact(
        "the worker waived no substitute tax regime in writing"
    ),
    "PriorYearTaxFacts.shortfall_deferral": absence_is_fact(
        "no written request to defer the shortfall"
    ),
    "PriorYearTaxFacts.foreign_taxes": absence_is_fact(
        "no foreign tax paid is declared for the art. 165 TUIR credit"
    ),
    "WorkCalendar.extra_months": absence_is_fact(
        "the calendar the caller builds has no extra month"
    ),
}
