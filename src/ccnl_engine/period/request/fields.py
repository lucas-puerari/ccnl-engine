"""Runtime type specifications for a period request."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    PublicEndOfService,
    WeeklyHours,
    WorkPattern,
)
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.employment.rest_day.inputs import Weekday
from ccnl_engine.employment.rota.inputs import Rota
from ccnl_engine.irpef.declaration.inputs import PriorYearTaxFacts
from ccnl_engine.irpef.other_income.inputs import CurrentYearTaxFacts
from ccnl_engine.pension_fund.inputs import PENSION_FUND_TYPES
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.seniority.inputs import SeniorityFact
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.validators import FieldSpec

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest


def period_request_fields(request: PeriodCalculationRequest) -> tuple[FieldSpec, ...]:
    """List the runtime-checked fields of the request.

    Returns:
        Name, value, accepted types and optionality of each field.
    """
    r = request
    return (
        ("ordinary_hours_worked", r.ordinary_hours_worked, ContributableHours, True),
        ("full_time_weekly_hours", r.full_time_weekly_hours, WeeklyHours, True),
        ("work_pattern", r.work_pattern, WorkPattern, True),
        ("weekly_rest_day", r.weekly_rest_day, Weekday, False),
        ("rota", r.rota, Rota, True),
        ("employment_period", r.employment_period, EmploymentPeriod, True),
        ("seniority", r.seniority, SeniorityFact, True),
        ("sector", r.sector, EmploymentSector, True),
        ("prior_year", r.prior_year, PriorYearTaxFacts, False),
        ("current_year", r.current_year, CurrentYearTaxFacts, True),
        ("pension_fund", r.pension_fund, PENSION_FUND_TYPES, True),
        ("tfr_fund", r.tfr_fund, TfrFundBalance, True),
        ("tfr_treasury_fund", r.tfr_treasury_fund, bool, True),
        ("erc_amount", r.erc_amount, Decimal, True),
        ("prior_extra_month_amount", r.prior_extra_month_amount, Decimal, True),
        ("public_end_of_service", r.public_end_of_service, PublicEndOfService, True),
    )
