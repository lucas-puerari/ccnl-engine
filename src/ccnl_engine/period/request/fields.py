"""Runtime type specifications for period calculation requests."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    WeeklyHours,
    WorkPattern,
)
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.employment.rest_day.inputs import Weekday
from ccnl_engine.employment.rota.inputs import Rota
from ccnl_engine.irpef.declaration.inputs import PriorYearTaxFacts
from ccnl_engine.irpef.other_income.inputs import CurrentYearTaxFacts
from ccnl_engine.pension_fund.inputs import PENSION_FUND_TYPES
from ccnl_engine.period.facts.holiday import PaidHolidayDays
from ccnl_engine.period.request.field_specs import contract_field_specs
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import SeniorityFact
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.validators import FieldSpec

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest


def period_field_specs(request: PeriodCalculationRequest) -> tuple[FieldSpec, ...]:
    """Return the fields an untyped caller may supply with a wrong type.

    Returns:
        One spec per checked field: name, value, types, ``None`` allowed.
    """
    return (
        ("period_id", request.period_id, PeriodId, False),
        ("payment_date", request.payment_date, date, False),
        ("ccnl_id", request.ccnl_id, str, False),
        ("level_code", request.level_code, str, False),
        ("level_started_on", request.level_started_on, date, True),
        ("opening_state", request.opening_state, PeriodState, False),
        *contract_field_specs(request),
        ("weekly_hours", request.weekly_hours, WeeklyHours, True),
        ("contributable_hours", request.contributable_hours, ContributableHours, True),
        (
            "ordinary_hours_worked",
            request.ordinary_hours_worked,
            ContributableHours,
            True,
        ),
        ("paid_holiday_days", request.paid_holiday_days, PaidHolidayDays, True),
        ("full_time_weekly_hours", request.full_time_weekly_hours, WeeklyHours, True),
        ("work_pattern", request.work_pattern, WorkPattern, True),
        ("weekly_rest_day", request.weekly_rest_day, Weekday, False),
        ("rota", request.rota, Rota, True),
        ("employment_period", request.employment_period, EmploymentPeriod, True),
        ("seniority", request.seniority, SeniorityFact, True),
        ("sector", request.sector, EmploymentSector, True),
        ("prior_year", request.prior_year, PriorYearTaxFacts, False),
        ("current_year", request.current_year, CurrentYearTaxFacts, True),
        ("pension_fund", request.pension_fund, PENSION_FUND_TYPES, True),
        ("tfr_fund", request.tfr_fund, TfrFundBalance, True),
        ("tfr_treasury_fund", request.tfr_treasury_fund, bool, True),
        ("erc_amount", request.erc_amount, Decimal, True),
        ("prior_extra_month_amount", request.prior_extra_month_amount, Decimal, True),
        ("holiday_company_offset", request.holiday_company_offset, Decimal, True),
    )
