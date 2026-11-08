"""Defaults of the per-run facts within a public period request."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, absence_is_fact, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

_REPORTED = FactEnforcement.REPORTED
_REQUIREMENT = FactEnforcement.REQUIREMENT

PERIOD_FACT_DEFAULTS: Mapping[str, FieldDefault] = {
    "PeriodFacts.ordinary_hours_worked": requires_fact(
        "pension_fund_contribution",
        "facts.ordinary_hours_worked",
        _REPORTED,
        "unknown hours: the pay of a worker a CCNL pays by the hour "
        "(hourly_pay) and the Prevedi contractual contribution of an operaio "
        "of the building CCNLs are left out, with a missing_fact "
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
    "PeriodFacts.meal_benefit_days": absence_is_fact(
        "no eligible electronic meal vouchers confirmed for the period; "
        "the caller supplies only days on which the employer, schedule, "
        "attendance and voucher medium have been verified"
    ),
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
