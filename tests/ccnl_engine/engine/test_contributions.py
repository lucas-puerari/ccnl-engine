"""Tests for engine.contributions — rate resolution, INPS and TFR calculations."""

from decimal import Decimal

import pytest

from ccnl_engine.engine.contributions import inps_contribution, resolve_rates, tfr
from ccnl_engine.engine.rounding import money
from ccnl_engine.models.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.tax.models import YearRules
from tests.conftest import make_domestic_year_rules, make_year_rules

_D = Decimal


def _rules(ceiling: str | None = None) -> YearRules:
    """Build minimal YearRules with configurable INPS ceiling.

    Returns:
        A YearRules instance with the specified ceiling value.
    """
    return make_year_rules(
        inps={
            "employee_rate": "0.0919",
            "employee_ivs_rate": "0.0919",
            "employer_rate": "0.2898",
            "employer_ivs_rate": "0.2381",
            "ceiling": ceiling,
            "employer_rate_by_category": {"impiegato": "0.2471"},
        },
        apprentice={
            "employee_rate": "0.0584",
            "employee_ivs_rate": "0.0584",
            "employer_rate_months_0_11": "0.0311",
            "employer_ivs_rate_months_0_11": "0.0150",
            "employer_rate_months_12_23": "0.0461",
            "employer_ivs_rate_months_12_23": "0.0300",
            "employer_rate_after": "0.1161",
            "employer_ivs_rate_after": "0.1000",
        },
    )


class TestResolveRates:
    """resolve_rates() by employment type and worker category."""

    def test_permanent(self) -> None:
        """Permanent: sector rates unchanged."""
        r = resolve_rates(_rules(), Permanent(), None)
        assert (r.employee_rate, r.employer_rate) == (_D("0.0919"), _D("0.2898"))

    def test_permanent_category_override(self) -> None:
        """Category-specific employer rate applies when the category matches."""
        assert resolve_rates(_rules(), Permanent(), "impiegato").employer_rate == _D(
            "0.2471"
        )
        assert resolve_rates(_rules(), Permanent(), "operaio").employer_rate == _D(
            "0.2898"
        )

    def test_fixed_term_adds_naspi(self) -> None:
        """Fixed-term: employer rate + fixed_term_additional_rate."""
        r = resolve_rates(_rules(), FixedTerm(), None)
        assert r.employer_rate == _D("0.3038")

    def test_apprentice_by_months(self) -> None:
        """Apprentice: statutory employee rate, employer rate stepping by months."""
        rules = _rules()
        assert resolve_rates(rules, Apprentice(months_elapsed=0), None) == (
            resolve_rates(rules, Apprentice(months_elapsed=11), None)
        )
        assert resolve_rates(
            rules, Apprentice(months_elapsed=0), None
        ).employee_rate == (_D("0.0584"))
        assert [
            resolve_rates(
                rules, Apprentice(months_elapsed=m), "impiegato"
            ).employer_rate
            for m in (0, 12, 24)
        ] == [_D("0.0311"), _D("0.0461"), _D("0.1161")]


class TestInpsContribution:
    """inps_contribution() with and without ceiling."""

    def test_uncapped_no_ceiling(self) -> None:
        """No ceiling configured: flat rate on the full base."""
        result = inps_contribution(
            _D("24972.50"),
            _D("0.0919"),
            _D("0.0919"),
            _rules(),
            ivs_ceiling_applies=True,
        )
        assert result == _D("2294.97")

    def test_ceiling_not_applies(self) -> None:
        """ivs_ceiling_applies=False: flat rate even when ceiling is set."""
        result = inps_contribution(
            _D("150000.00"),
            _D("0.3050"),
            _D("0.2381"),
            _rules("119650.00"),
            ivs_ceiling_applies=False,
        )
        assert result == _D("150000.00") * _D("0.3050")

    def test_ceiling_base_below(self) -> None:
        """Ceiling applies but base < ceiling: IVS and non-IVS both on full base."""
        total_rate = _D("0.3050")
        ivs_rate = _D("0.2381")
        base = _D("80000.00")
        result = inps_contribution(
            base,
            total_rate,
            ivs_rate,
            _rules("119650.00"),
            ivs_ceiling_applies=True,
        )
        assert result == base * total_rate

    def test_ceiling_base_above_splits_correctly(self) -> None:
        """Ceiling applies and base > ceiling: IVS portion capped, non-IVS uncapped."""
        total_rate = _D("0.3050")
        ivs_rate = _D("0.2381")
        non_ivs_rate = total_rate - ivs_rate
        base = _D("150000.00")
        ceiling = _D("119650.00")
        result = inps_contribution(
            base,
            total_rate,
            ivs_rate,
            _rules("119650.00"),
            ivs_ceiling_applies=True,
        )
        expected = money(ceiling * ivs_rate + base * non_ivs_rate)
        assert result == expected


class TestTfr:
    """tfr() accrual."""

    def test_standard(self) -> None:
        """TFR = base / 13.5, rounded to nearest cent."""
        assert tfr(_D("24972.50"), _rules()) == _D("1849.81")


class TestResolveRatesGuard:
    """resolve_rates() raises when rules.inps or rules.apprentice is None."""

    def test_none_inps_raises(self) -> None:
        """Domestic rules (inps=None) must raise TypeError from resolve_rates."""
        domestic_rules = make_domestic_year_rules()
        with pytest.raises(TypeError, match="resolve_rates requires standard INPS"):
            resolve_rates(domestic_rules, Permanent(), None)
