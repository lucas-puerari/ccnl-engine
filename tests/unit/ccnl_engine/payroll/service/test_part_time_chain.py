"""Unit tests for MonthlyPayChain.scaled_for_part_time and part_time_proportionable."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.engine.contract.domain.compensation import Allowance
from ccnl_engine.engine.contract.domain.validity import TimeSeries
from ccnl_engine.payroll.service.types import MonthlyPayChain


def _series(value: str) -> dict[object, object]:
    return {
        "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": value}]
    }


def _ts(value: str) -> TimeSeries:
    return TimeSeries.model_validate(_series(value))


def _allowance(
    code: str = "EDR",
    monthly: str = "100.00",
    *,
    part_time_proportionable: bool = True,
) -> Allowance:
    return Allowance(
        code=code,
        description=code,
        monthly=_ts(monthly),
        part_time_proportionable=part_time_proportionable,
    )


class TestScaledForPartTime:
    """MonthlyPayChain.scaled_for_part_time respects the proportionable flag."""

    def test_non_proportionable_allowance_unchanged(self) -> None:
        """A fixed allowance keeps its full value when the chain is scaled."""
        a_prop = _allowance("PROP", "100.00", part_time_proportionable=True)
        a_fixed = _allowance("FIXED", "50.00", part_time_proportionable=False)
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("60.00"),
            allowances=((a_prop, Decimal("100.00")), (a_fixed, Decimal("50.00"))),
        )
        result = chain.scaled_for_part_time(Decimal("0.5"))
        assert result.base == Decimal("500.00")
        assert result.seniority == Decimal("30.00")
        assert result.allowances[0][1] == Decimal("50.00")
        assert result.allowances[1][1] == Decimal("50.00")

    def test_all_proportionable_equals_scaled(self) -> None:
        """When all allowances are proportionable, scaled_for_part_time == scaled."""
        a = _allowance(part_time_proportionable=True)
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("50.00"),
            allowances=((a, Decimal("100.00")),),
        )
        factor = Decimal("0.5")
        assert chain.scaled_for_part_time(factor) == chain.scaled(factor)
