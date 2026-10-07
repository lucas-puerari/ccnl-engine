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


def _dependent(fact: str, reason: str) -> FieldDefault:
    return requires_fact("family_deductions", fact, _REPORTED, reason)


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
        "own_income",
        "unknown own income (art. 12 c. 2 TUIR): a dependant that may qualify "
        "takes no deduction and the run has a missing_fact own_income "
        "blocker; it also leaves the fringe-benefit threshold of a child open",
    ),
    "Dependent.allocation_pct": _dependent(
        "allocation_pct",
        "unknown share of a child or an ascendant (art. 12 c. 1 lett. c and "
        "d TUIR): no deduction and a missing_fact allocation_pct blocker; a "
        "spouse takes the whole deduction",
    ),
    "Dependent.cohabiting": _dependent(
        "cohabiting",
        "unknown cohabitation of an ascendant (art. 12 c. 1 lett. d TUIR): no "
        "deduction and a missing_fact cohabiting blocker",
    ),
    "Dependent.residency_eligibility": _dependent(
        "residency_eligibility",
        "unknown condition of art. 12 c. 2-bis TUIR: a dependant that may "
        "qualify takes no deduction and the run has a missing_fact "
        "residency_eligibility blocker",
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
        "other_employers",
        _REPORTED,
        "unknown base of other employments: a run whose INPS rules carry a "
        "massimale the worker may be subject to or a 1% threshold has a "
        "missing_fact other_employers blocker; 0 states none",
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
    "OpeningBalances.sickness_episodes": _IMPORTED_LIST,
    **{f"OpeningBalances.{name}": _ACCOUNT for name in _ACCOUNTS},
    **{f"OpeningBalances.{name}": _NOT_COMPUTED for name in _LAST_COMPUTED},
    "OpeningBalances.employment_spells": absence_is_fact(
        "the totals hold no earlier employment of the tax year: the next run "
        "adds the days of its own"
    ),
    "OpeningBalances.deferred_shortfall": absence_is_fact(
        "no written request to defer the shortfall (art. 23 c. 3 DPR 600/1973)"
    ),
    "PeriodState.accrual": absence_is_fact(
        "a state built by the caller starts from empty accrual accounts; the "
        "opening state of a run is classified on PeriodInput"
    ),
    "PeriodState.history_known": absence_is_fact(
        "a state the caller builds states the history of the employment; the "
        "engine marks the closing state of a run opened without it"
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
