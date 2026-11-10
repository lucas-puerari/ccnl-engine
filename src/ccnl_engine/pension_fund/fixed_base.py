"""Resolve a fund's sourced fixed monthly contribution base by level."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.fund.models import FundContributionBase
from ccnl_engine.pension_fund.enrolment.rules import in_force
from ccnl_engine.pension_fund.inputs import PENSION_FEATURE

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.fund.models import EmployerFund


def fixed_level_base(fund: EmployerFund, level_code: str | None, day: date) -> Decimal:
    """Return the dated base or reject a missing level instead of using current pay.

    Returns:
        The historical fixed base for this level and date.

    Raises:
        InvalidInputError: When the fund has no base for the given level and date.
    """
    if fund.contribution_base is not FundContributionBase.FIXED_BY_LEVEL:
        return Decimal(0)
    level_series = fund.fixed_base_by_level.get(level_code or "")
    level_base = in_force(level_series, day)
    if level_base is None:
        msg = f"fund {fund.code} lacks a fixed base for {level_code} on {day}"
        raise InvalidInputError(msg, feature=PENSION_FEATURE)
    return level_base[1]
