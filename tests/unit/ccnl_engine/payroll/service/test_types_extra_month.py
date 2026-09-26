"""MonthlyPayChain.for_extra_month keeps the allowances an extra month pays."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.compensation import Allowance
from ccnl_engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.payroll.service.types import MonthlyPayChain


class TestForExtraMonth:
    """MonthlyPayChain.for_extra_month filters allowances by months_per_year."""

    def _make_allowance(self, code: str, months_per_year: int | None) -> Allowance:
        ts = TimeSeries(
            periods=(
                ValidityPeriod(
                    value=Decimal("10.00"),
                    valid_from=date(2024, 1, 1),
                    valid_until=None,
                ),
            )
        )
        return Allowance(
            code=code,
            description=code,
            monthly=ts,
            months_per_year=months_per_year,
        )

    def test_no_allowances_unchanged(self) -> None:
        """Chain with no allowances passes through unchanged."""
        chain = MonthlyPayChain(
            base=Decimal(1000), seniority=Decimal(50), allowances=()
        )
        result = chain.for_extra_month(13)
        assert result.base == chain.base
        assert result.seniority == chain.seniority
        assert result.allowances == ()

    def test_allowance_with_none_mpy_always_included(self) -> None:
        """Allowance with months_per_year=None is included in any extra-month run."""
        a = self._make_allowance("ALL", months_per_year=None)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(13)
        assert len(result.allowances) == 1

    def test_allowance_with_12_mpy_excluded_for_thirteenth(self) -> None:
        """Allowance with months_per_year=12 is excluded from thirteenth run."""
        a = self._make_allowance("EDR", months_per_year=12)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(13)
        assert result.allowances == ()

    def test_allowance_with_13_mpy_included_for_thirteenth(self) -> None:
        """Allowance with months_per_year=13 is included in thirteenth run."""
        a = self._make_allowance("BONUS13", months_per_year=13)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(13)
        assert len(result.allowances) == 1

    def test_allowance_with_12_mpy_excluded_for_fourteenth(self) -> None:
        """Allowance with months_per_year=12 is excluded from fourteenth run."""
        a = self._make_allowance("EDR", months_per_year=12)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(14)
        assert result.allowances == ()

    def test_allowance_with_13_mpy_excluded_for_fourteenth(self) -> None:
        """Allowance with months_per_year=13 is excluded from fourteenth run."""
        a = self._make_allowance("BONUS13", months_per_year=13)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(14)
        assert result.allowances == ()

    def test_allowance_with_14_mpy_included_for_fourteenth(self) -> None:
        """Allowance with months_per_year=14 is included in fourteenth run."""
        a = self._make_allowance("BONUS14", months_per_year=14)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a, Decimal(10)),),
        )
        result = chain.for_extra_month(14)
        assert len(result.allowances) == 1

    def test_mixed_allowances_filtered_correctly(self) -> None:
        """Only eligible allowances remain after filtering."""
        a12 = self._make_allowance("EDR", months_per_year=12)
        a13 = self._make_allowance("BONUS13", months_per_year=13)
        chain = MonthlyPayChain(
            base=Decimal(1000),
            seniority=Decimal(0),
            allowances=((a12, Decimal(10)), (a13, Decimal(20))),
        )
        result = chain.for_extra_month(13)
        assert len(result.allowances) == 1
        assert result.allowances[0][0].code == "BONUS13"
