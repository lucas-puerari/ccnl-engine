"""Defaults of the request and plan types exported at the package root."""

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

__all__ = ["REQUEST_DEFAULTS"]

_REQUIREMENT = FactEnforcement.REQUIREMENT
_REPORTED = FactEnforcement.REPORTED
_PENDING = FactEnforcement.PENDING

_CONTAINER = absence_is_fact(
    "an empty container: each of its own fields is classified on its own"
)
_CURRENT_YEAR = requires_fact(
    "family_deductions",
    "current_year",
    _REPORTED,
    "unknown income beyond this employment: with a dependant that gives right "
    "to a deduction, or a somma esente due on this employment alone, the run "
    "has a missing_fact current_year blocker; the INPS base of other "
    "employments stays unknown unless the opening state states it",
)
_OPENING_STATE = requires_fact(
    "irpef",
    "opening_state",
    _REPORTED,
    "the zero state, a fact only for the first run of an employment whose "
    "start is stated: a later run, or one of an employment whose start is "
    "not stated, has a missing_fact opening_state blocker",
)

_FIRST_RUN = absence_is_fact(
    "the first run of its kind in the month; only a second or later "
    "adjustment of the same month has another number"
)

#: Classification of each defaulted field of the root request types.
REQUEST_DEFAULTS: Mapping[str, FieldDefault] = {
    "PeriodInput.facts": _CONTAINER,
    "PeriodInput.prior_year": _CONTAINER,
    "PeriodInput.current_year": _CURRENT_YEAR,
    "PeriodInput.opening_state": _OPENING_STATE,
    "PeriodInput.planned_payments": absence_is_fact(
        "the standard runs of the CCNL calendar follow this run; another "
        "calendar is a fact the caller states"
    ),
    "CompetenceYearPlan.prior_year": _CONTAINER,
    "CompetenceYearPlan.current_year": _CURRENT_YEAR,
    "CompetenceYearPlan.periods": absence_is_fact("every run takes default_facts"),
    "CompetenceYearPlan.default_facts": _CONTAINER,
    "CompetenceYearPlan.calendar_override": absence_is_fact(
        "the standard calendar of the CCNL applies"
    ),
    "CompetenceYearPlan.payment_day": absence_is_fact(
        "each run is paid within its own month, so in the tax year of the month"
    ),
    "CompetenceYearPlan.payment_dates": absence_is_fact(
        "each run is paid on payment_day of its own month, a quattordicesima "
        "on the day its CCNL fixes"
    ),
    "CompetenceYearPlan.opening_state": _OPENING_STATE,
    "PayrollRun.sequence": _FIRST_RUN,
    "PayrollRunId.sequence": _FIRST_RUN,
    "TaxYearPlan.opening_state": _OPENING_STATE,
    "TaxYearPlan.current_year": _CURRENT_YEAR,
    "EmployerProfile.activity": requires_fact(
        "notte_festivi_turni_substitute_tax",
        "employer.activity",
        _REPORTED,
        "unknown activity: the regime that excludes some activities is "
        "undetermined, with a blocker",
    ),
    "Employment.category": requires_fact(
        "worker_category",
        "employment.category",
        _REPORTED,
        "the category the level fixes; a level that leaves it open raises "
        "when the seniority or the INPS rates differ by category, and has a "
        "missing_fact category blocker when its sector excludes a category "
        "from the INPS minimum base and the pay is below it",
    ),
    "Employment.employment_period": requires_fact(
        "base_salary",
        "employment.employment_period",
        _PENDING,
        "an employment whose start is not stated: a full month and full "
        "ratei without a blocker, even for a hire or a termination within the "
        "month; a run after the first has a missing_fact opening_state blocker "
        "unless its opening state is stated",
    ),
    "Employment.weekly_hours": requires_fact(
        "base_salary",
        "employment.weekly_hours",
        _PENDING,
        "full time, without a blocker; a domestic CCNL raises "
        "MissingRequiredFactError without it",
    ),
    "Employment.full_time_weekly_hours": requires_fact(
        "base_salary",
        "employment.full_time_weekly_hours",
        _REPORTED,
        "unknown full time: with weekly_hours stated the part-time fraction is "
        "undetermined and the run has a missing_fact full_time_weekly_hours "
        "blocker; without weekly_hours it is not read",
    ),
    "Employment.seniority": requires_fact(
        "seniority",
        "employment.seniority",
        _REPORTED,
        "unknown recognised seniority: a missing_fact seniority blocker",
    ),
    "Employment.roles": requires_fact(
        "base_salary",
        "employment.roles",
        _REPORTED,
        "unknown roles: a run whose level has an allowance restricted to a role "
        "in force leaves it out and has a missing_fact roles blocker; an empty "
        "set states that the worker holds no role",
    ),
    "Employment.contribution_history": requires_fact(
        "inps_employee",
        "employment.contribution_history",
        _REPORTED,
        "unknown first enrolment: a run whose base crosses the IVS massimale "
        "has a missing_fact contribution_history blocker",
    ),
    "Employment.sector": requires_fact(
        "rinnovo_substitute_tax",
        "employment.sector",
        _REPORTED,
        "unknown sector: the renewal regime of the private sector is "
        "undetermined, with a blocker",
    ),
    "Employment.tfr_fund": requires_fact(
        "tfr_revaluation",
        "employment.tfr_fund",
        _REPORTED,
        "unknown TFR fund at 31 December of the year before: the December run "
        "of an employment that did not start in the year has a missing_fact "
        "tfr_fund blocker",
    ),
    "Employment.tfr_treasury_fund": requires_fact(
        "tfr",
        "employment.tfr_treasury_fund",
        _REPORTED,
        "unknown Fondo Tesoreria destination: a run that accrues TFR outside "
        "a pension fund has a missing_fact tfr_treasury_fund blocker",
    ),
    "Employment.public_end_of_service": requires_fact(
        "inps_employee",
        "employment.public_end_of_service",
        _REPORTED,
        "unknown end-of-service regime: a run on a CCNL of the public "
        "administrations leaves out the contributions to INPS Gestione "
        "Dipendenti Pubblici and has a missing_fact public_end_of_service "
        "blocker",
    ),
    "Employment.erc_amount": requires_fact(
        "pension_fund_contribution",
        "employment.erc_amount",
        _REPORTED,
        "unknown ERC of the CCNL grafici editoriali (zero for an employment "
        "started after December 2020): an enrolment in Byblos "
        "uses the 1.9% rate of a worker without it, a run paying the "
        "tredicesima leaves the ERC out, and the run has a missing_fact "
        "erc_amount blocker",
    ),
    "Employment.pension_fund": requires_fact(
        "pension_fund_contribution",
        "employment.pension_fund",
        _REPORTED,
        "unknown enrolment: on every CCNL but domestic work the contributions "
        "are undetermined and the run has a missing_fact pension_fund blocker; "
        "NoPensionFund states the non-enrolment",
    ),
    "PeriodFacts.ordinary_hours_worked": requires_fact(
        "pension_fund_contribution",
        "facts.ordinary_hours_worked",
        _REPORTED,
        "unknown hours: the Prevedi contractual contribution of an operaio "
        "of the building CCNLs is left out, with a missing_fact "
        "ordinary_hours_worked blocker; other CCNLs do not read it",
    ),
    "PeriodFacts.contributable_hours": requires_fact(
        "inps_employee",
        "facts.contributable_hours",
        _REPORTED,
        "a domestic CCNL raises MissingRequiredFactError without it; other "
        "CCNLs do not read it",
    ),
    "PeriodFacts.events": absence_is_fact("no work event in the period"),
    "PeriodFacts.regione": requires_fact(
        "addizionale_regionale",
        "facts.regione",
        _REQUIREMENT,
        "unknown residence: the regional surtax is not ruled out",
    ),
    "PeriodFacts.comune_belfiore": requires_fact(
        "addizionale_comunale",
        "facts.comune_belfiore",
        _REQUIREMENT,
        "unknown residence: the municipal surtax is not ruled out",
    ),
    "PeriodFacts.family_composition": requires_fact(
        "family_deductions",
        "facts.family_composition",
        _REQUIREMENT,
        "unknown family: the art. 12 TUIR deductions are not ruled out; an "
        "empty FamilyComposition states that there is no dependant",
    ),
}
