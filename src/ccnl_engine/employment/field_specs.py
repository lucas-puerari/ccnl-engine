"""Runtime type specifications for the employment relationship."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.employment.fact.inputs import WeeklyHours, WorkPattern
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.pension_fund.inputs import PENSION_FUND_TYPES
from ccnl_engine.seniority.inputs import SeniorityFact
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.validators import FieldSpec

if TYPE_CHECKING:
    from ccnl_engine.employment.inputs import Employment


def employment_fields(
    employment: Employment, contract_types: tuple[type, ...]
) -> tuple[FieldSpec, ...]:
    """List the runtime-checked fields of the employment.

    Returns:
        Name, value, accepted types and optionality of each field.
    """
    e = employment
    return (
        ("contract_type", e.contract_type, contract_types, False),
        ("employment_period", e.employment_period, EmploymentPeriod, True),
        ("level_started_on", e.level_started_on, date, True),
        ("weekly_hours", e.weekly_hours, WeeklyHours, True),
        ("full_time_weekly_hours", e.full_time_weekly_hours, WeeklyHours, True),
        ("work_pattern", e.work_pattern, WorkPattern, True),
        ("seniority", e.seniority, SeniorityFact, True),
        ("contribution_history", e.contribution_history, ContributionHistory, True),
        ("pension_fund", e.pension_fund, PENSION_FUND_TYPES, True),
        ("prior_extra_month_amount", e.prior_extra_month_amount, Decimal, True),
        ("tfr_fund", e.tfr_fund, TfrFundBalance, True),
        ("tfr_treasury_fund", e.tfr_treasury_fund, bool, True),
    )
