"""Allowance activation by role and service months."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.compensation import Allowance
from ccnl_engine.contract.domain.validity import (
    SalaryGapKind,
    TimeSeries,
    ValidityPeriod,
)
from ccnl_engine.payroll.service.chain import _allowance_active
from tests.helpers import _series

_DAY = date(2026, 6, 1)


def _time_series(value: str) -> TimeSeries:
    """Build a single-period TimeSeries for the given value.

    Returns:
        A :class:`TimeSeries` valid from 2020-01-01 with no end date.
    """
    return TimeSeries.model_validate(_series(value))


def _allowance(
    *,
    code: str = "EDR",
    monthly: str = "10.00",
    role: str | None = None,
    apprenticeship_pct_relevant: bool = True,
    service_months_threshold: int | None = None,
) -> Allowance:
    """Build a minimal :class:`Allowance` for testing.

    Returns:
        A frozen :class:`Allowance` with the given parameters.
    """
    return Allowance(
        code=code,
        description=code,
        monthly=_time_series(monthly),
        role=role,
        apprenticeship_pct_relevant=apprenticeship_pct_relevant,
        service_months_threshold=service_months_threshold,
        provenance=None,
    )


class TestAllowanceActive:
    """_allowance_active branching logic."""

    def test_role_not_in_roles_returns_false(self) -> None:
        """Returns False when the allowance has a role not present in roles."""
        a = _allowance(role="manager")
        assert _allowance_active(a, frozenset({"driver"}), None, _DAY) is False

    def test_no_role_no_threshold_returns_true(self) -> None:
        """Returns True when role is None and threshold is None."""
        a = _allowance(role=None, service_months_threshold=None)
        assert _allowance_active(a, frozenset(), None, _DAY) is True

    def test_threshold_met(self) -> None:
        """Returns True when seniority_months >= service_months_threshold."""
        a = _allowance(service_months_threshold=12)
        assert _allowance_active(a, frozenset(), 24, _DAY) is True

    def test_threshold_not_met(self) -> None:
        """Returns False when seniority_months < service_months_threshold."""
        a = _allowance(service_months_threshold=24)
        assert _allowance_active(a, frozenset(), 12, _DAY) is False

    def test_not_in_force_returns_false(self) -> None:
        """Returns False in a ``not_applicable`` gap, before the rule exists."""
        monthly = TimeSeries(
            periods=(
                ValidityPeriod(
                    valid_from=date(2024, 1, 1),
                    valid_until=date(2025, 7, 1),
                    gap_kind=SalaryGapKind.NOT_APPLICABLE,
                ),
                ValidityPeriod(
                    valid_from=date(2025, 7, 1), valid_until=None, value=Decimal(30)
                ),
            )
        )
        a = _allowance().model_copy(update={"monthly": monthly})
        assert _allowance_active(a, frozenset(), None, date(2025, 6, 1)) is False
        assert _allowance_active(a, frozenset(), None, date(2025, 7, 1)) is True
