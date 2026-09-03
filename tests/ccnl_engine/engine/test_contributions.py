"""Tests for engine.contributions — rate resolution, INPS and TFR calculations."""

from decimal import Decimal

from ccnl_engine.engine.contributions import inps_contribution, resolve_rates, tfr
from ccnl_engine.models.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.tax.models import YearRules
from tests.conftest import make_year_rules

_D = Decimal


def _rules(ceiling: str | None = None) -> YearRules:
    """Build minimal YearRules with configurable INPS ceiling.

    Returns:
        A YearRules instance with the specified ceiling value.
    """
    return make_year_rules(
        inps={
            "employee_rate": "0.0919",
            "employer_rate": "0.2898",
            "ceiling": ceiling,
            "employer_rate_by_category": {"impiegato": "0.2471"},
        },
        apprentice={
            "employee_rate": "0.0584",
            "employer_rate_months_0_11": "0.0311",
            "employer_rate_months_12_23": "0.0461",
            "employer_rate_after": "0.1161",
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

    def test_uncapped(self) -> None:
        """No ceiling: contribution is base * rate, rounded to the cent."""
        result = inps_contribution(_D("24972.50"), _D("0.0919"), _rules())
        assert result == _D("2294.97")

    def test_ceiling_base_below(self) -> None:
        """Ceiling set and base < ceiling: base is unchanged."""
        result = inps_contribution(_D("24000.00"), _D("0.0919"), _rules("30000.00"))
        assert result == _D("24000.00") * _D("0.0919")

    def test_ceiling_base_above(self) -> None:
        """Ceiling set and base > ceiling: base is capped at ceiling."""
        result = inps_contribution(_D("24000.00"), _D("0.0919"), _rules("20000.00"))
        assert result == _D("20000.00") * _D("0.0919")


class TestTfr:
    """tfr() accrual."""

    def test_standard(self) -> None:
        """TFR = base / 13.5, rounded to nearest cent."""
        assert tfr(_D("24972.50"), _rules()) == _D("1849.81")
