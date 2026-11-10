"""Defaults of the request and plan types exported at the package root."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, absence_is_fact, requires_fact
from ccnl_engine.default.request.period_facts import PERIOD_FACT_DEFAULTS
from ccnl_engine.default.request.role_policies import ROLE_DEFAULTS

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["REQUEST_DEFAULTS"]

_REQUIREMENT = FactEnforcement.REQUIREMENT
_REPORTED = FactEnforcement.REPORTED
_PENDING = FactEnforcement.PENDING

_CONTAINER = absence_is_fact("an empty container: its fields are classified")
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
    "Apprentice.programme": absence_is_fact(
        "a professionalising apprenticeship (D.Lgs. 81/2015 art. 44), the one "
        "the apprenticeship tracks of the CCNL pay"
    ),
    "Apprentice.school_year": requires_fact(
        "base_salary",
        "employment.contract_type.school_year",
        _REPORTED,
        "unknown school year: a dual track paying by it raises a missing-fact error",
    ),
    "Apprentice.programme_months": requires_fact(
        "base_salary",
        "employment.contract_type.programme_months",
        _REPORTED,
        "unknown programme length: a dual track paying by its half or length "
        "raises a missing-fact error",
    ),
    "Apprentice.hours": requires_fact(
        "base_salary",
        "employment.contract_type.hours",
        _REPORTED,
        "unknown hours: a first- or third-level apprentice raises a missing-fact error",
    ),
    "Apprentice.track": requires_fact(
        "base_salary",
        "employment.contract_type.track",
        _REPORTED,
        "the unique track of the level; several tracks raise an input error",
    ),
    "Apprentice.failed_title_extension_start_month": absence_is_fact(
        "ordinary apprenticeship progression, or a competence-consolidation "
        "extension; a failed-title extension is a fact the caller states, "
        "and only a sourced first-level track can pay its previous-year phase"
    ),
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
    "CompetenceYearPlan.employment_changes": absence_is_fact("same terms all year"),
    "EmploymentChange.level_code": absence_is_fact("the level is kept"),
    "EmploymentChange.weekly_hours": absence_is_fact("the hours are kept"),
    "EmploymentChange.category": absence_is_fact("the category is kept"),
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
    "Employment.category": requires_fact(
        "worker_category",
        "employment.category",
        _REPORTED,
        "the category the level fixes; a level that leaves it open raises "
        "when the seniority differs by category, takes the general employer "
        "rate with an employer_rate_category_assumed blocker when the INPS "
        "rates differ by category, and has a missing_fact category blocker "
        "when its sector excludes a category from the INPS minimum base and "
        "the pay is below it",
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
    "Employment.full_time_week_days": absence_is_fact(
        "the daily divisor of the CCNL absence rule, whatever the week"
    ),
    "Employment.rota": absence_is_fact(
        "the leave days of the CCNL default rota (FEDERDAT: 5+1, 25 days)"
    ),
    "Employment.qualifying_shifts": requires_fact(
        "leave",
        "employment.qualifying_shifts",
        _PENDING,
        "unknown rotation: where a CCNL grants additional PAR hours to a "
        "worker in at least 15 weekly shifts including night and/or weekend "
        "work, the base PAR is credited but its balance is inexact; when the "
        "shift clause cannot grant leave (before its effective date or for "
        "sectors paid instead) the missing shift fact does not affect leave",
    ),
    "Employment.work_pattern": absence_is_fact(
        "a horizontal part time or a full time: every month is worked and "
        "weekly_hours alone sets the part-time ratio"
    ),
    "Employment.weekly_rest_day": absence_is_fact(
        "the rest on Sunday, the day of L. 370/1934 art. 3"
    ),
    "Employment.individual_elements": absence_is_fact("no element above the minimo"),
    "Employment.personal_withholdings": absence_is_fact("no order notified"),
    "PersonalWithholding.installment": absence_is_fact("a legal fraction, none stated"),
    "IndividualElement.absorbable": absence_is_fact("not absorbed by increases"),
    "IndividualElement.as_of": absence_is_fact("read only when absorbable"),
    "IndividualElement.extra_months": absence_is_fact("paid on the extra months"),
    "IndividualElement.tfr_relevant": absence_is_fact("in the TFR base"),
    "SeniorityFact.earned": absence_is_fact("the table prices every increment"),
    "SeniorityFact.promotion": absence_is_fact("no promotion since the last increment"),
    "Permanent.entry_pay": absence_is_fact("the pay of the level, no entry pay"),
    "SeniorityFact.birth_date": requires_fact(
        "seniority",
        "seniority.birth_date",
        _PENDING,
        "an adult hire: on a CCNL that counts the increments from an age the "
        "service counts from the start, without a blocker",
    ),
    "EmploymentPeriod.uninterrupted_service_started_on": requires_fact(
        "base_salary",
        "employment_period.uninterrupted_service_started_on",
        _PENDING,
        "the hire date stands for uninterrupted actual service when no separate "
        "start is supplied; conventional seniority and breaks are not inferred",
    ),
    "EmploymentPeriod.probation_until": requires_fact(
        "contractual_funds",
        "employment_period.probation_until",
        _PENDING,
        "no probation: a fund that leaves it out is charged from the hire",
    ),
    "SeniorityFact.career_months": requires_fact(
        "base_salary",
        "seniority.career_months",
        _PENDING,
        "the service months stand for the career of a career-gated allowance",
    ),
    "SeniorityFact.apprenticeship_months": requires_fact(
        "seniority",
        "seniority.apprenticeship_months",
        _REPORTED,
        "unknown past apprenticeship duration: a CCNL that credits a share "
        "towards increments shows the service alone, a lower bound, with a "
        "missing_fact apprenticeship_months blocker; zero confirms no "
        "preceding apprenticeship",
    ),
    "Employment.level_started_on": requires_fact(
        "base_salary",
        "employment.level_started_on",
        _REPORTED,
        "an entry-level transition needs the level entry date; missing in "
        "Confetra 6J before 2026, the pay is provisional and blocked; "
        "an allowance gated on months in the level also needs this date: "
        "without it the allowance is omitted and the run has a missing_fact "
        "level_started_on blocker",
    ),
    "Employment.seniority": requires_fact(
        "seniority",
        "employment.seniority",
        _REPORTED,
        "unknown recognised seniority: a missing_fact seniority blocker",
    ),
    **ROLE_DEFAULTS,
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
    "Employment.prior_extra_month_amount": requires_fact(
        "base_salary",
        "employment.prior_extra_month_amount",
        _REPORTED,
        "unknown extra remuneration already received at contract entry: "
        "a fourteenth payment for a worker employed by the entry date "
        "has a missing_fact prior_extra_month_amount blocker; zero states none, "
        "merit awards do not count",
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
    **PERIOD_FACT_DEFAULTS,
}
