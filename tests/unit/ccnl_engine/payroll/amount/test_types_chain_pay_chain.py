"""MonthlyPayChain scaling, extra-month filtering and totals."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.contract.compensation.models import Allowance
from ccnl_engine.contract.identity.rules_validity import TimeSeries
from ccnl_engine.payroll.amount.types_chain import MonthlyPayChain
from tests.helpers import _series


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


class TestMonthlyPayChain:
    """MonthlyPayChain.scaled, for_extra_month, allowances_total."""

    def test_scaled_applies_factor_to_all_components(self) -> None:
        """scaled() multiplies base, seniority, and all allowances by factor."""
        a = _allowance(monthly="100.00")
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("50.00"),
            allowances=((a, Decimal("100.00")),),
        )
        result = chain.scaled(Decimal("0.5"))
        assert result.base == Decimal("500.00")
        assert result.seniority == Decimal("25.00")
        assert result.allowances[0][1] == Decimal("50.00")

    def test_prorated_rounds_each_component_once(self) -> None:
        """14/26 of 2,158.26, 50.00 and 2.06, each rounded to the cent.

        2,158.26 x 14 / 26 = 1,162.14; 50.00 x 14 / 26 = 26.923 -> 26.92;
        2.06 x 14 / 26 = 1.109 -> 1.11.
        """
        a = _allowance(monthly="2.06")
        chain = MonthlyPayChain(
            base=Decimal("2158.26"),
            seniority=Decimal("50.00"),
            allowances=((a, Decimal("2.06")),),
            limitations=("limit",),
        )
        result = chain.prorated(Decimal(14), Decimal(26))
        assert result.base == Decimal("1162.14")
        assert result.seniority == Decimal("26.92")
        assert result.allowances[0][1] == Decimal("1.11")
        assert result.limitations == ("limit",)

    def test_for_extra_month_filters_by_months_per_year(self) -> None:
        """for_extra_month excludes allowances paid fewer than threshold times/year."""
        a_all = _allowance(code="ALL", monthly="10.00")
        a_12 = Allowance(
            code="A12",
            description="A12",
            monthly=_time_series("10.00"),
            months_per_year=12,
        )
        a_14 = Allowance(
            code="A14",
            description="A14",
            monthly=_time_series("10.00"),
            months_per_year=14,
        )
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("0.00"),
            allowances=(
                (a_all, Decimal("10.00")),
                (a_12, Decimal("10.00")),
                (a_14, Decimal("10.00")),
            ),
        )
        result = chain.for_extra_month(13)
        codes = {a.code for a, _ in result.allowances}
        assert "ALL" in codes
        assert "A12" not in codes
        assert "A14" in codes

    def test_allowances_total_sums_all_values(self) -> None:
        """allowances_total returns the rounded sum of all allowance amounts."""
        a1 = _allowance(code="A1", monthly="10.00")
        a2 = _allowance(code="A2", monthly="20.00")
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("0.00"),
            allowances=((a1, Decimal("10.00")), (a2, Decimal("20.00"))),
        )
        assert chain.allowances_total == Decimal("30.00")
