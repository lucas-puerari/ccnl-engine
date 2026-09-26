"""Domestic INPS hourly rates: bracket lookup and field constraints."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.payroll.service._contributions_domestic import (
    resolve_domestic_inps_rate,
)
from ccnl_engine.tax.domain.domestic_contribution_rules import DomesticInpsRates
from tests.helpers import (
    DOMESTIC_CONTRIBUTIONS,
)

_DOMESTIC_RATES = DomesticInpsRates.model_validate(DOMESTIC_CONTRIBUTIONS)


class TestDomesticInpsRates:
    """DomesticInpsRates.resolve() — all selector branches."""

    def test_hours_bracket_permanent(self) -> None:
        """weekly_hours > 24 → hours bracket, permanent rate."""
        emp, er = resolve_domestic_inps_rate(
            _DOMESTIC_RATES, Decimal("8.00"), Decimal(40), is_fixed_term=False
        )
        assert emp == Decimal("0.31")
        assert er == Decimal("0.93")

    def test_hours_bracket_fixed_term(self) -> None:
        """weekly_hours > 24 → hours bracket, fixed-term employer rate."""
        emp, er = resolve_domestic_inps_rate(
            _DOMESTIC_RATES, Decimal("8.00"), Decimal(30), is_fixed_term=True
        )
        assert emp == Decimal("0.31")
        assert er == Decimal("1.01")

    def test_wage_bracket_low_permanent(self) -> None:
        """hourly_rate <= 9.61 + weekly_hours <= 24 → lowest wage bracket."""
        emp, er = resolve_domestic_inps_rate(
            _DOMESTIC_RATES, Decimal("8.00"), Decimal(20), is_fixed_term=False
        )
        assert emp == Decimal("0.43")
        assert er == Decimal("1.27")

    def test_wage_bracket_mid_fixed_term(self) -> None:
        """9.61 < hourly_rate <= 11.70, weekly_hours <= 24 → mid bracket, ft."""
        emp, er = resolve_domestic_inps_rate(
            _DOMESTIC_RATES, Decimal("10.00"), Decimal(20), is_fixed_term=True
        )
        assert emp == Decimal("0.48")
        assert er == Decimal("1.57")

    def test_wage_bracket_high_permanent(self) -> None:
        """hourly_rate > 11.70 + weekly_hours <= 24 → highest bracket."""
        emp, er = resolve_domestic_inps_rate(
            _DOMESTIC_RATES, Decimal("15.00"), Decimal(24), is_fixed_term=False
        )
        assert emp == Decimal("0.59")
        assert er == Decimal("1.75")

    def test_domestic_rates_missing_open_bracket_raises(self) -> None:
        """DomesticInpsRates rejects wage_brackets without an open-ended last entry."""
        with pytest.raises(ValidationError, match="hourly_rate_up_to=None"):
            DomesticInpsRates.model_validate({
                "weekly_hours_threshold": 24,
                "hours_bracket": {
                    "employee_per_hour": "0.31",
                    "employer_per_hour": "0.93",
                    "employer_per_hour_fixed_term": "1.01",
                },
                "wage_brackets": [
                    {
                        "hourly_rate_up_to": "9.61",
                        "employee_per_hour": "0.43",
                        "employer_per_hour": "1.27",
                        "employer_per_hour_fixed_term": "1.39",
                    },
                ],
            })

    def test_domestic_rates_open_bracket_not_last_raises(self) -> None:
        """DomesticInpsRates rejects an open bracket that is not the last entry."""
        with pytest.raises(ValidationError, match="not the last bracket"):
            DomesticInpsRates.model_validate({
                "weekly_hours_threshold": 24,
                "hours_bracket": {
                    "employee_per_hour": "0.31",
                    "employer_per_hour": "0.93",
                    "employer_per_hour_fixed_term": "1.01",
                },
                "wage_brackets": [
                    {
                        "hourly_rate_up_to": None,
                        "employee_per_hour": "0.43",
                        "employer_per_hour": "1.27",
                        "employer_per_hour_fixed_term": "1.39",
                    },
                    {
                        "hourly_rate_up_to": "11.70",
                        "employee_per_hour": "0.48",
                        "employer_per_hour": "1.44",
                        "employer_per_hour_fixed_term": "1.57",
                    },
                ],
            })


class TestDomesticInpsRatesNegativeConstraints:
    """DomesticInpsRates must reject negative thresholds and non-ascending brackets."""

    _HOURS_BRACKET: dict[str, str] = {
        "employee_per_hour": "0.31",
        "employer_per_hour": "0.93",
        "employer_per_hour_fixed_term": "1.01",
    }

    def test_negative_weekly_hours_threshold_raises(self) -> None:
        """weekly_hours_threshold < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            DomesticInpsRates.model_validate({
                "weekly_hours_threshold": -1,
                "hours_bracket": self._HOURS_BRACKET,
                "wage_brackets": [
                    {
                        "hourly_rate_up_to": None,
                        "employee_per_hour": "0.43",
                        "employer_per_hour": "1.27",
                        "employer_per_hour_fixed_term": "1.39",
                    },
                ],
            })

    def test_non_ascending_wage_brackets_raises(self) -> None:
        """Wage brackets with non-ascending hourly_rate_up_to must raise."""
        with pytest.raises(
            ValidationError, match="strictly ascending hourly_rate_up_to"
        ):
            DomesticInpsRates.model_validate({
                "weekly_hours_threshold": 24,
                "hours_bracket": self._HOURS_BRACKET,
                "wage_brackets": [
                    {
                        "hourly_rate_up_to": "11.70",
                        "employee_per_hour": "0.48",
                        "employer_per_hour": "1.44",
                        "employer_per_hour_fixed_term": "1.57",
                    },
                    {
                        "hourly_rate_up_to": "9.61",
                        "employee_per_hour": "0.43",
                        "employer_per_hour": "1.27",
                        "employer_per_hour_fixed_term": "1.39",
                    },
                    {
                        "hourly_rate_up_to": None,
                        "employee_per_hour": "0.59",
                        "employer_per_hour": "1.75",
                        "employer_per_hour_fixed_term": "1.87",
                    },
                ],
            })
