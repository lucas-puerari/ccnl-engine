"""Default policies for facts supplied for one payroll period."""

from ccnl_engine.default.models import (
    FactEnforcement,
    FieldDefault,
    absence_is_fact,
    requires_fact,
)

_PERIOD_REPORTED = FactEnforcement.REPORTED
_PERIOD_REQUIREMENT = FactEnforcement.REQUIREMENT

PERIOD_FACT_DEFAULTS: dict[str, FieldDefault] = {
    "PeriodFacts.ordinary_hours_worked": requires_fact(
        "pension_fund_contribution",
        "facts.ordinary_hours_worked",
        _PERIOD_REPORTED,
        "unknown hours: the pay of a worker a CCNL pays by the hour "
        "(hourly_pay) and the Prevedi contractual contribution of an operaio "
        "of the building CCNLs are left out, with a missing_fact "
        "ordinary_hours_worked blocker; other CCNLs do not read it",
    ),
    "PeriodFacts.paid_holiday_days": absence_is_fact(
        "no eligible holiday days stated: the hourly pay omits the holiday "
        "treatment unless the caller supplies the count, including locally "
        "eligible days; no date or suspension eligibility is inferred"
    ),
    "PeriodFacts.contributable_hours": requires_fact(
        "inps_employee",
        "facts.contributable_hours",
        _PERIOD_REPORTED,
        "a domestic CCNL raises MissingRequiredFactError without it; other "
        "CCNLs do not read it",
    ),
    "PeriodFacts.presence_days": requires_fact(
        "base_salary",
        "facts.presence_days",
        _PERIOD_REPORTED,
        "unknown actual presence days: a regular run with a qualifying daily "
        "allowance leaves that earning out and reports a missing_fact "
        "presence_days blocker; zero states no days present",
    ),
    "PeriodFacts.site_presence_days": requires_fact(
        "base_salary",
        "facts.site_presence_days",
        _PERIOD_REPORTED,
        "unknown work-site presence days: only a worker qualifying for a "
        "site-based daily allowance has a missing_fact site_presence_days "
        "blocker; zero states no days at the site",
    ),
    "PeriodFacts.events": absence_is_fact("no work event in the period"),
    "PeriodFacts.regione": requires_fact(
        "addizionale_regionale",
        "facts.regione",
        _PERIOD_REQUIREMENT,
        "unknown residence: the regional surtax is not ruled out",
    ),
    "PeriodFacts.comune_belfiore": requires_fact(
        "addizionale_comunale",
        "facts.comune_belfiore",
        _PERIOD_REQUIREMENT,
        "unknown residence: the municipal surtax is not ruled out",
    ),
    "PeriodFacts.family_composition": requires_fact(
        "family_deductions",
        "facts.family_composition",
        _PERIOD_REQUIREMENT,
        "unknown family: the art. 12 TUIR deductions are not ruled out; an "
        "empty FamilyComposition states that there is no dependant",
    ),
}
