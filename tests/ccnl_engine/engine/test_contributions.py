"""Tests for engine.contributions — INPS and TFR calculations.

100 % branch coverage: exercises ceiling=None vs ceiling-set, and
fixed_term=False vs fixed_term=True paths.
"""

from decimal import Decimal

from ccnl_engine.engine.contributions import inps_employee, inps_employer, tfr
from ccnl_engine.tax.models import InpsRates, TfrRules, YearRules

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_VALID_BRACKETS = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": None, "rate": "0.43"},
]
_VALID_DEDUCTIONS = [
    {"income_up_to": None, "deduction": "0.00"},
]


def _rules(ceiling: str | None = None) -> YearRules:
    """Build minimal YearRules with configurable INPS ceiling."""
    return YearRules.model_validate(
        {
            "year": 2026,
            "irpef_brackets": _VALID_BRACKETS,
            "work_deduction_breakpoints": _VALID_DEDUCTIONS,
            "fixed_term_additional_rate": "0.014",
            "inps": {
                "employee_rate": "0.0919",
                "employer_rate": "0.2898",
                "ceiling": ceiling,
            },
            "tfr": {"accrual_divisor": "13.5"},
        }
    )


# ---------------------------------------------------------------------------
# inps_employee
# ---------------------------------------------------------------------------


class TestInpsEmployee:
    """Unit tests for inps_employee()."""

    def test_uncapped(self) -> None:
        """No ceiling: contribution is gross_annual * employee_rate."""
        rules = _rules(ceiling=None)
        result = inps_employee(Decimal("24972.50"), rules)
        # 24972.50 * 0.0919 = 2294.97275 → 2294.97
        assert result == Decimal("2294.97")

    def test_ceiling_gross_below(self) -> None:
        """Ceiling set and gross < ceiling: base is gross_annual."""
        rules = _rules(ceiling="30000.00")
        result = inps_employee(Decimal("24000.00"), rules)
        assert result == Decimal("24000.00") * Decimal("0.0919")
        assert result == inps_employee(Decimal("24000.00"), _rules(ceiling=None))

    def test_ceiling_gross_above(self) -> None:
        """Ceiling set and gross > ceiling: base is capped at ceiling."""
        rules = _rules(ceiling="20000.00")
        result = inps_employee(Decimal("24000.00"), rules)
        # base is capped at 20000
        assert result == Decimal("20000.00") * Decimal("0.0919")


# ---------------------------------------------------------------------------
# inps_employer
# ---------------------------------------------------------------------------


class TestInpsEmployer:
    """Unit tests for inps_employer()."""

    def test_permanent_uncapped(self) -> None:
        """No ceiling, permanent: contribution uses full employer_rate."""
        rules = _rules(ceiling=None)
        result = inps_employer(Decimal("24972.50"), rules, fixed_term=False)
        # 24972.50 * 0.2898 = 7234.82
        expected = (Decimal("24972.50") * Decimal("0.2898")).quantize(Decimal("0.01"))
        assert result == expected

    def test_fixed_term_adds_naspi(self) -> None:
        """Fixed-term: employer_rate + fixed_term_additional_rate applied."""
        rules = _rules(ceiling=None)
        result_fixed = inps_employer(Decimal("10000.00"), rules, fixed_term=True)
        result_perm = inps_employer(Decimal("10000.00"), rules, fixed_term=False)
        # Difference must be 10000 * 0.014 = 140.00
        assert result_fixed - result_perm == Decimal("140.00")

    def test_ceiling_gross_above(self) -> None:
        """Ceiling set and gross > ceiling: base is capped."""
        rules = _rules(ceiling="20000.00")
        result = inps_employer(Decimal("24000.00"), rules, fixed_term=False)
        assert result == Decimal("20000.00") * Decimal("0.2898")

    def test_ceiling_gross_below(self) -> None:
        """Ceiling set and gross <= ceiling: base is gross_annual."""
        rules = _rules(ceiling="30000.00")
        result = inps_employer(Decimal("24000.00"), rules, fixed_term=False)
        uncapped = inps_employer(
            Decimal("24000.00"), _rules(ceiling=None), fixed_term=False
        )
        assert result == uncapped


# ---------------------------------------------------------------------------
# tfr
# ---------------------------------------------------------------------------


class TestTfr:
    """Unit tests for tfr()."""

    def test_standard(self) -> None:
        """TFR = gross_annual / 13.5, rounded to nearest cent."""
        rules = _rules()
        result = tfr(Decimal("24972.50"), rules)
        # 24972.50 / 13.5 = 1849.814... → 1849.81
        assert result == Decimal("1849.81")

    def test_tfr_rules_standalone(self) -> None:
        """TfrRules model stores the accrual_divisor correctly."""
        tr = TfrRules(accrual_divisor=Decimal("13.5"))
        assert tr.accrual_divisor == Decimal("13.5")

    def test_inps_rates_standalone(self) -> None:
        """InpsRates model stores rates correctly."""
        ir = InpsRates(
            employee_rate=Decimal("0.0919"),
            employer_rate=Decimal("0.2898"),
            ceiling=None,
        )
        assert ir.ceiling is None
