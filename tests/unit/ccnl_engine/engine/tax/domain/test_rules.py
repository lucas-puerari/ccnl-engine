"""Tests for ccnl_engine.engine.tax.models.

Covers every branch in YearRules validators and tests that the canonical
2026-terziario.json data file loads correctly via load_year_rules.
"""

from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.engine.primitives import Bracket
from ccnl_engine.engine.tax.domain.rules import (
    ApprenticeRates,
    ApprenticeRawRates,
    DeductionBreakpoint,
    DomesticInpsRates,
    InpsEmployeeTier,
    InpsEmployerTier,
    InpsRates,
    InpsRawRates,
    IrpefBracket,
    SommaEsenteBand,
    SommaEsenteRules,
    TfrRules,
    YearRules,
    YearRulesRaw,
)
from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates, SickPayBand
from ccnl_engine.engine.tax.service.loaders import (
    _assert_tier_integrity,
    _resolve_tier,
    load_year_rules,
    read_inps_rules_raw,
    read_tax_rules_raw,
)
from ccnl_engine.payroll.service.contributions import (
    apprentice_employer_rate,
    inps_employer_rate,
    resolve_domestic_inps_rate,
)
from tests.helpers import (
    DOMESTIC_CONTRIBUTIONS,
    IRPEF_BRACKETS_2026,
)

# ---------------------------------------------------------------------------
# Minimal valid fixture helpers
# ---------------------------------------------------------------------------

_VALID_BRACKETS: list[dict[str, Any]] = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]

_VALID_INPS: dict[str, Any] = {
    "employee_rate": "0.0919",
    "employee_ivs_rate": "0.0919",
    "employer_rate": "0.2898",
    "employer_ivs_rate": "0.2381",
    "ceiling": None,
}

_VALID_APPRENTICE: dict[str, Any] = {
    "employee_rate": "0.0584",
    "employee_ivs_rate": "0.0584",
    "employer_rate_months_0_11": "0.0311",
    "employer_ivs_rate_months_0_11": "0.0150",
    "employer_rate_months_12_23": "0.0461",
    "employer_ivs_rate_months_12_23": "0.0300",
    "employer_rate_after": "0.1161",
    "employer_ivs_rate_after": "0.1000",
}


def _year_rules(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a minimal valid YearRules dict, with optional field overrides.

    Returns:
        A dict suitable for passing to YearRules.model_validate().
    """
    base: dict[str, Any] = {
        "year": 2026,
        "irpef_brackets": _VALID_BRACKETS,
        "fixed_term_additional_rate": "0.014",
        "inps": _VALID_INPS,
        "apprentice": _VALID_APPRENTICE,
        "tfr": {"accrual_divisor": "13.5"},
    }
    if overrides:
        base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# IrpefBracket
# ---------------------------------------------------------------------------


class TestBracketRateConstraint:
    """Bracket.__post_init__ rejects rates outside [0, 1]."""

    def test_valid_rate_accepted(self) -> None:
        """Rate in [0, 1] is accepted."""
        b = Bracket(up_to=Decimal(28000), rate=Decimal("0.23"))
        assert b.rate == Decimal("0.23")

    def test_zero_rate_accepted(self) -> None:
        """rate=0 is on the boundary and must be accepted."""
        b = Bracket(up_to=None, rate=Decimal(0))
        assert b.rate == Decimal(0)

    def test_one_rate_accepted(self) -> None:
        """rate=1 is on the boundary and must be accepted."""
        b = Bracket(up_to=None, rate=Decimal(1))
        assert b.rate == Decimal(1)

    def test_negative_rate_raises(self) -> None:
        """Rate < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="\\[0, 1\\]"):
            Bracket(up_to=None, rate=Decimal("-0.23"))

    def test_rate_above_one_raises(self) -> None:
        """Rate > 1 must raise ValueError."""
        with pytest.raises(ValueError, match="\\[0, 1\\]"):
            Bracket(up_to=None, rate=Decimal("1.01"))


class TestIrpefBracket:
    """Unit tests for IrpefBracket construction."""

    def test_bounded_bracket(self) -> None:
        """A bracket with a finite up_to is accepted."""
        b = IrpefBracket(up_to=Decimal(28000), rate=Decimal("0.23"))
        assert b.up_to == Decimal(28000)

    def test_unbounded_bracket(self) -> None:
        """A bracket with up_to=None (unbounded) is accepted."""
        b = IrpefBracket(up_to=None, rate=Decimal("0.43"))
        assert b.up_to is None


# ---------------------------------------------------------------------------
# DeductionBreakpoint
# ---------------------------------------------------------------------------


class TestDeductionBreakpoint:
    """Unit tests for DeductionBreakpoint construction."""

    def test_finite_breakpoint(self) -> None:
        """A breakpoint with a finite income_up_to is accepted."""
        p = DeductionBreakpoint(income_up_to=Decimal(8500), deduction=Decimal(1955))
        assert p.income_up_to == Decimal(8500)

    def test_open_ended_breakpoint(self) -> None:
        """A breakpoint with income_up_to=None (open-ended) is accepted."""
        p = DeductionBreakpoint(income_up_to=None, deduction=Decimal(0))
        assert p.income_up_to is None


# ---------------------------------------------------------------------------
# InpsRates
# ---------------------------------------------------------------------------


class TestInpsTiers:
    """Unit tests for InpsEmployeeTier and InpsEmployerTier ivs_rate validator."""

    def test_employee_tier_ivs_rate_exceeds_rate_raises(self) -> None:
        """ivs_rate > rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="ivs_rate"):
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.09"), ivs_rate=Decimal("0.10")
            )

    def test_employer_tier_ivs_rate_exceeds_rate_raises(self) -> None:
        """ivs_rate > rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="ivs_rate"):
            InpsEmployerTier(
                max_employees=None, rate=Decimal("0.28"), ivs_rate=Decimal("0.30")
            )

    def test_employer_tier_category_rate_below_ivs_rate_raises(self) -> None:
        """rate_by_category value < ivs_rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="rate_by_category"):
            InpsEmployerTier(
                max_employees=None,
                rate=Decimal("0.2693"),
                ivs_rate=Decimal("0.2381"),
                rate_by_category={"impiegato": Decimal("0.20")},
            )


class TestInpsRates:
    """Unit tests for InpsRates construction."""

    def test_uncapped(self) -> None:
        """ceiling=None (no cap) is accepted."""
        r = InpsRates(
            employee_rate=Decimal("0.0919"),
            employee_ivs_rate=Decimal("0.0919"),
            employer_rate=Decimal("0.2898"),
            employer_ivs_rate=Decimal("0.2381"),
            ceiling=None,
        )
        assert r.ceiling is None

    def test_with_ceiling(self) -> None:
        """A finite ceiling is accepted."""
        r = InpsRates(
            employee_rate=Decimal("0.09"),
            employee_ivs_rate=Decimal("0.09"),
            employer_rate=Decimal("0.28"),
            employer_ivs_rate=Decimal("0.2381"),
            ceiling=Decimal(105014),
        )
        assert r.ceiling == Decimal(105014)

    def test_employer_rate_for_category(self) -> None:
        """Category override applies only to listed categories."""
        r = InpsRates(
            employee_rate=Decimal("0.0919"),
            employee_ivs_rate=Decimal("0.0919"),
            employer_rate=Decimal("0.2693"),
            employer_ivs_rate=Decimal("0.2381"),
            ceiling=None,
            employer_rate_by_category={"impiegato": Decimal("0.2471")},
        )
        assert inps_employer_rate(r, None) == Decimal("0.2693")
        assert inps_employer_rate(r, "operaio") == Decimal("0.2693")
        assert inps_employer_rate(r, "impiegato") == Decimal("0.2471")


# ---------------------------------------------------------------------------
# ApprenticeRates
# ---------------------------------------------------------------------------


class TestApprenticeRates:
    """Unit tests for ApprenticeRates.employer_rate_at() and ivs_rate validators."""

    def test_rate_steps(self) -> None:
        """Employer rate steps at month 12 and month 24."""
        r = ApprenticeRates.model_validate(_VALID_APPRENTICE)
        assert apprentice_employer_rate(r, 0) == Decimal("0.0311")
        assert apprentice_employer_rate(r, 11) == Decimal("0.0311")
        assert apprentice_employer_rate(r, 12) == Decimal("0.0461")
        assert apprentice_employer_rate(r, 23) == Decimal("0.0461")
        assert apprentice_employer_rate(r, 24) == Decimal("0.1161")

    def test_ivs_rate_exceeds_total_raises(self) -> None:
        """Any ivs_rate above its paired total rate must raise ValidationError."""
        with pytest.raises(ValidationError, match=r"ivs_rate.*must not exceed"):
            ApprenticeRates.model_validate({
                **_VALID_APPRENTICE,
                "employer_ivs_rate_after": "0.20",
            })


class TestApprenticeRawRates:
    """ivs_rate validators on ApprenticeRawRates (raw JSON model)."""

    _VALID_RAW: dict[str, Any] = {
        "employee_rate": "0.0584",
        "employee_ivs_rate": "0.0584",
        "employer_rate": "0.1161",
        "employer_ivs_rate": "0.1000",
        "small_firm_max_employees": 9,
        "small_firm_employer_rate_months_0_11": "0.0311",
        "small_firm_employer_ivs_rate_months_0_11": "0.0150",
        "small_firm_employer_rate_months_12_23": "0.0461",
        "small_firm_employer_ivs_rate_months_12_23": "0.0300",
    }

    def test_ivs_rate_exceeds_total_raises(self) -> None:
        """employer_ivs_rate above employer_rate must raise ValidationError."""
        with pytest.raises(ValidationError, match=r"ivs_rate.*must not exceed"):
            ApprenticeRawRates.model_validate({
                **self._VALID_RAW,
                "employer_ivs_rate": "0.20",  # exceeds employer_rate 0.1161
            })


# ---------------------------------------------------------------------------
# YearRules — IRPEF bracket validators
# ---------------------------------------------------------------------------


class TestYearRulesIrpefBrackets:
    """YearRules validation for irpef_brackets."""

    def test_valid_three_brackets(self) -> None:
        """Three brackets with ascending up_to and open-ended last are valid."""
        yr = YearRules.model_validate(_year_rules())
        assert len(yr.irpef_brackets) == 3
        assert yr.irpef_brackets[-1].up_to is None

    def test_empty_brackets_raises(self) -> None:
        """An empty irpef_brackets list must raise ValidationError."""
        with pytest.raises(ValidationError, match="irpef_brackets must not be empty"):
            YearRules.model_validate(_year_rules({"irpef_brackets": []}))

    def test_non_last_bracket_open_ended_raises(self) -> None:
        """An intermediate bracket with up_to=None must raise ValidationError."""
        bad = [
            {"up_to": None, "rate": "0.23"},
            {"up_to": None, "rate": "0.43"},
        ]
        with pytest.raises(ValidationError, match="only the last irpef_bracket"):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_non_ascending_up_to_raises(self) -> None:
        """Non-ascending up_to values must raise ValidationError."""
        bad = [
            {"up_to": "50000.00", "rate": "0.23"},
            {"up_to": "28000.00", "rate": "0.33"},
            {"up_to": None, "rate": "0.43"},
        ]
        with pytest.raises(ValidationError, match="strictly ascending up_to"):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_last_bracket_not_open_ended_raises(self) -> None:
        """A last bracket with finite up_to must raise ValidationError."""
        bad = [
            {"up_to": "28000.00", "rate": "0.23"},
            {"up_to": "50000.00", "rate": "0.43"},
        ]
        with pytest.raises(
            ValidationError, match="last irpef_bracket must be unbounded"
        ):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_single_open_ended_bracket_valid(self) -> None:
        """A single unbounded bracket is valid (loop body never executes)."""
        single = [{"up_to": None, "rate": "0.23"}]
        yr = YearRules.model_validate(_year_rules({"irpef_brackets": single}))
        assert len(yr.irpef_brackets) == 1

    def test_two_brackets_second_open_ended_skips_ascending_check(self) -> None:
        """With two brackets, the ascending check is skipped for the last pair."""
        two = [
            {"up_to": "28000.00", "rate": "0.23"},
            {"up_to": None, "rate": "0.43"},
        ]
        yr = YearRules.model_validate(_year_rules({"irpef_brackets": two}))
        assert len(yr.irpef_brackets) == 2


# ---------------------------------------------------------------------------
# YearRules — deduction breakpoint validators
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# YearRules — 2026.json round-trip
# ---------------------------------------------------------------------------


class TestYearRules2026Json:
    """Validates that the 2026-terziario.json data file loads via load_year_rules."""

    def test_2026_json_loads(self) -> None:
        """load_year_rules(2026, terziario, 50) must return correct YearRules."""
        yr = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert yr.year == 2026
        assert len(yr.irpef_brackets) == 3
        assert yr.irpef_brackets[0].rate == Decimal("0.23")
        assert yr.irpef_brackets[1].rate == Decimal("0.33")
        assert yr.irpef_brackets[2].rate == Decimal("0.43")
        assert yr.inps is not None
        assert yr.inps.employee_rate == Decimal("0.0919")
        assert yr.inps.employer_rate == Decimal("0.2898")
        assert yr.inps.ceiling == Decimal("122295.00")
        assert yr.fixed_term_additional_rate == Decimal("0.014")
        assert yr.tfr.accrual_divisor == Decimal("13.5")
        assert yr.apprentice is not None
        assert yr.apprentice.employer_rate_after == Decimal("0.1161")
        assert yr.apprentice.employer_rate_months_0_11 == Decimal("0.1161")

    def test_employee_tier_above_threshold(self) -> None:
        """Terziario above 50 employees: employee +0.30% CIGS, employer 29.58%."""
        yr = load_year_rules(2026, TaxSector.TERZIARIO, 51)
        assert yr.inps is not None
        assert yr.inps.employee_rate == Decimal("0.0949")
        assert yr.inps.employer_rate == Decimal("0.2958")

    def test_small_firm_apprentice_rates(self) -> None:
        """Firms with at most 9 employees get the reduced apprentice rates."""
        yr = load_year_rules(2026, TaxSector.TERZIARIO, 9)
        assert yr.apprentice is not None
        assert yr.apprentice.employer_rate_months_0_11 == Decimal("0.0311")
        assert yr.apprentice.employer_rate_months_12_23 == Decimal("0.0461")
        assert yr.apprentice.employer_rate_after == Decimal("0.1161")

    def test_artigianato_category_rates(self) -> None:
        """Artigianato: lower employer rate for impiegati/quadri (kitech.it source)."""
        yr = load_year_rules(2026, TaxSector.ARTIGIANATO, 10)
        assert yr.inps is not None
        assert yr.inps.employer_rate_by_category == {
            "impiegato": Decimal("0.2471"),
            "quadro": Decimal("0.2471"),
        }

    def test_domestic_2026_loads(self) -> None:
        """load_year_rules(2026, LAVORO_DOMESTICO, 1) returns domestic_contributions."""
        yr = load_year_rules(2026, TaxSector.LAVORO_DOMESTICO, 1)
        assert yr.inps is None
        assert yr.apprentice is None
        assert yr.domestic_contributions is not None
        assert yr.domestic_contributions.weekly_hours_threshold == 24
        assert yr.domestic_contributions.hours_bracket.employee_per_hour == Decimal(
            "0.31"
        )

    def test_no_open_tier_raises(self) -> None:
        """_assert_tier_integrity raises when no open tier is present."""
        tiers = [
            InpsEmployeeTier(
                max_employees=10, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            )
        ]
        with pytest.raises(DataIntegrityError, match="exactly one open tier"):
            _assert_tier_integrity(tiers, "employee")

    def test_no_open_tier_covered_headcount_still_raises(self) -> None:
        """_assert_tier_integrity raises even when headcount fits a bounded tier."""
        tiers = [
            InpsEmployeeTier(
                max_employees=10, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            )
        ]
        # Without the fix, headcount=5 would succeed; now it must fail
        # because the structural defect (no open band) is caught up front.
        with pytest.raises(DataIntegrityError, match="exactly one open tier"):
            _resolve_tier(tiers, 5, "employee")

    def test_single_open_tier_accepted(self) -> None:
        """_assert_tier_integrity accepts a list with exactly one open tier."""
        tiers = [
            InpsEmployeeTier(
                max_employees=15, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            ),
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.10"), ivs_rate=Decimal("0.09")
            ),
        ]
        # Must not raise; verifies the happy path.
        _assert_tier_integrity(tiers, "employee")

    def test_multiple_open_tiers_raises(self) -> None:
        """_assert_tier_integrity raises when more than one open tier exists."""
        tiers = [
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            ),
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.10"), ivs_rate=Decimal("0.09")
            ),
        ]
        with pytest.raises(DataIntegrityError, match=r"exactly one open tier"):
            _assert_tier_integrity(tiers, "employee")

    def test_duplicate_max_employees_raises(self) -> None:
        """_assert_tier_integrity raises if max_employees values are duplicated."""
        tiers = [
            InpsEmployeeTier(
                max_employees=15, rate=Decimal("0.09"), ivs_rate=Decimal("0.09")
            ),
            InpsEmployeeTier(
                max_employees=15, rate=Decimal("0.10"), ivs_rate=Decimal("0.09")
            ),
            InpsEmployeeTier(
                max_employees=None, rate=Decimal("0.11"), ivs_rate=Decimal("0.09")
            ),
        ]
        with pytest.raises(DataIntegrityError, match="duplicate max_employees=15"):
            _assert_tier_integrity(tiers, "employee")

    def test_tfr_rules(self) -> None:
        """TfrRules accrual_divisor is parsed as Decimal."""
        tfr = TfrRules(accrual_divisor=Decimal("13.5"))
        assert tfr.accrual_divisor == Decimal("13.5")

    def test_tfr_rules_zero_divisor_raises(self) -> None:
        """TfrRules rejects accrual_divisor=0."""
        with pytest.raises(ValidationError, match="greater than 0"):
            TfrRules(accrual_divisor=Decimal(0))

    def test_tfr_rules_negative_divisor_raises(self) -> None:
        """TfrRules rejects negative accrual_divisor."""
        with pytest.raises(ValidationError, match="greater than 0"):
            TfrRules(accrual_divisor=Decimal(-1))


class TestSickPayBandInvariants:
    """SickPayBand and InpsSickPayRates construction-time validators."""

    def test_sick_pay_band_valid(self) -> None:
        """SickPayBand with day_to >= day_from is accepted."""
        band = SickPayBand(day_from=4, day_to=20, rate=Decimal("0.50"))
        assert band.day_to >= band.day_from

    def test_sick_pay_band_day_to_lt_day_from_raises(self) -> None:
        """SickPayBand rejects day_to < day_from."""
        with pytest.raises(ValidationError, match=r"day_to.*day_from"):
            SickPayBand(day_from=10, day_to=5, rate=Decimal("0.50"))

    def test_inps_sick_pay_rates_valid(self) -> None:
        """InpsSickPayRates with carenza=3 and ordered non-overlapping bands."""
        rates = InpsSickPayRates(
            carenza_days=3,
            bands=[
                SickPayBand(day_from=4, day_to=20, rate=Decimal("0.50")),
                SickPayBand(day_from=21, day_to=180, rate=Decimal("0.6667")),
            ],
        )
        assert len(rates.bands) == 2

    def test_inps_sick_pay_rates_empty_bands_ok(self) -> None:
        """InpsSickPayRates with no bands is accepted (no coverage modelled)."""
        rates = InpsSickPayRates(carenza_days=3, bands=[])
        assert rates.bands == []

    def test_inps_sick_pay_rates_first_band_wrong_start_raises(self) -> None:
        """First band must start at carenza_days + 1."""
        with pytest.raises(ValidationError, match="first band day_from"):
            InpsSickPayRates(
                carenza_days=3,
                bands=[SickPayBand(day_from=5, day_to=20, rate=Decimal("0.50"))],
            )

    def test_inps_sick_pay_rates_overlapping_bands_raise(self) -> None:
        """Overlapping bands are rejected."""
        with pytest.raises(ValidationError, match="overlaps"):
            InpsSickPayRates(
                carenza_days=3,
                bands=[
                    SickPayBand(day_from=4, day_to=20, rate=Decimal("0.50")),
                    SickPayBand(day_from=15, day_to=30, rate=Decimal("0.6667")),
                ],
            )

    def test_inps_sick_pay_rates_gap_between_bands_raises(self) -> None:
        """A gap between consecutive bands is rejected."""
        with pytest.raises(ValidationError, match="gap"):
            InpsSickPayRates(
                carenza_days=3,
                bands=[
                    SickPayBand(day_from=4, day_to=20, rate=Decimal("0.50")),
                    SickPayBand(day_from=25, day_to=180, rate=Decimal("0.6667")),
                ],
            )


_DOMESTIC_RATES = DomesticInpsRates.model_validate(DOMESTIC_CONTRIBUTIONS)

_RAW_BASE: dict[str, Any] = {
    "year": 2026,
    "sector": "terziario",
    "irpef_brackets": IRPEF_BRACKETS_2026,
    "fixed_term_additional_rate": "0.014",
    "tfr": {"accrual_divisor": "13.5"},
}


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


class TestInpsRatesNegativeConstraints:
    """InpsRates and related models must reject negative rates and ceilings."""

    def test_negative_employee_rate_raises(self) -> None:
        """employee_rate < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRates(
                employee_rate=Decimal("-0.1"),
                employee_ivs_rate=Decimal("-0.2"),
                employer_rate=Decimal("-0.1"),
                employer_ivs_rate=Decimal("-0.2"),
                ceiling=None,
            )

    def test_negative_ceiling_raises(self) -> None:
        """Ceiling < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRates(
                employee_rate=Decimal("0.0919"),
                employee_ivs_rate=Decimal("0.0919"),
                employer_rate=Decimal("0.2898"),
                employer_ivs_rate=Decimal("0.2381"),
                ceiling=Decimal(-1),
            )

    def test_zero_ceiling_raises(self) -> None:
        """Ceiling = 0 must raise ValidationError (must be strictly positive)."""
        with pytest.raises(ValidationError):
            InpsRates(
                employee_rate=Decimal("0.0919"),
                employee_ivs_rate=Decimal("0.0919"),
                employer_rate=Decimal("0.2898"),
                employer_ivs_rate=Decimal("0.2381"),
                ceiling=Decimal(0),
            )


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


class TestInpsRawRatesEmptyTiers:
    """InpsRawRates rejects empty employee_tiers or employer_tiers."""

    _OPEN_EMPLOYEE_TIER: dict[str, Any] = {
        "max_employees": None,
        "rate": "0.0919",
        "ivs_rate": "0.0919",
    }
    _OPEN_EMPLOYER_TIER: dict[str, Any] = {
        "max_employees": None,
        "rate": "0.2898",
        "ivs_rate": "0.2381",
    }

    def test_empty_employee_tiers_raises(self) -> None:
        """Empty employee_tiers must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRawRates.model_validate({
                "employee_tiers": [],
                "employer_tiers": [self._OPEN_EMPLOYER_TIER],
                "ceiling": None,
            })

    def test_empty_employer_tiers_raises(self) -> None:
        """Empty employer_tiers must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRawRates.model_validate({
                "employee_tiers": [self._OPEN_EMPLOYEE_TIER],
                "employer_tiers": [],
                "ceiling": None,
            })

    def test_non_empty_tiers_accepted(self) -> None:
        """Non-empty tiers are accepted."""
        raw = InpsRawRates.model_validate({
            "employee_tiers": [self._OPEN_EMPLOYEE_TIER],
            "employer_tiers": [self._OPEN_EMPLOYER_TIER],
            "ceiling": None,
        })
        assert len(raw.employee_tiers) == 1
        assert len(raw.employer_tiers) == 1


class TestYearRulesRawContributionModel:
    """YearRulesRaw validator: must have inps+apprentice or domestic_contributions."""

    def test_missing_both_raises(self) -> None:
        """Neither inps+apprentice nor domestic_contributions → ValidationError."""
        with pytest.raises(ValidationError, match="domestic_contributions"):
            YearRulesRaw.model_validate(_RAW_BASE)

    def test_both_models_raises(self) -> None:
        """R21: having both standard and domestic models is rejected."""
        # Merge a real standard-sector tax + inps dict (guaranteed parseable),
        # then also inject domestic_contributions to trigger the
        # mutual-exclusion guard.
        tax = read_tax_rules_raw(2026, TaxSector.TERZIARIO)
        inps = read_inps_rules_raw(2026, TaxSector.TERZIARIO)
        both = {**tax, **inps, "domestic_contributions": DOMESTIC_CONTRIBUTIONS}
        with pytest.raises(ValidationError, match="mutually exclusive"):
            YearRulesRaw.model_validate(both)

    def test_inps_without_apprentice_raises(self) -> None:
        """'inps' present without 'apprentice' must raise ValidationError."""
        inps = read_inps_rules_raw(2026, TaxSector.TERZIARIO)
        # Build a base with 'inps' but no 'apprentice'.
        data = {**_RAW_BASE, "inps": inps["inps"]}
        with pytest.raises(ValidationError, match="both absent"):
            YearRulesRaw.model_validate(data)

    def test_apprentice_without_inps_raises(self) -> None:
        """'apprentice' present without 'inps' must raise ValidationError."""
        inps_raw = read_inps_rules_raw(2026, TaxSector.TERZIARIO)
        data = {**_RAW_BASE, "apprentice": inps_raw["apprentice"]}
        with pytest.raises(ValidationError, match="both absent"):
            YearRulesRaw.model_validate(data)


class TestYearRulesContributionModel:
    """YearRules validator mirrors YearRulesRaw contribution-model checks."""

    def test_inps_without_apprentice_raises(self) -> None:
        """'inps' without 'apprentice' in YearRules must raise ValidationError."""
        with pytest.raises(ValidationError, match="both absent"):
            YearRules.model_validate(_year_rules({"apprentice": None}))

    def test_no_model_raises(self) -> None:
        """Neither model in YearRules must raise ValidationError."""
        with pytest.raises(ValidationError, match="standard model"):
            YearRules.model_validate(_year_rules({"inps": None, "apprentice": None}))

    def test_standard_and_domestic_raises(self) -> None:
        """Mixing standard and domestic in YearRules must raise ValidationError."""
        with pytest.raises(ValidationError, match="mutually exclusive"):
            YearRules.model_validate(
                _year_rules({"domestic_contributions": DOMESTIC_CONTRIBUTIONS})
            )


# ---------------------------------------------------------------------------
# InpsRates: IVS invariants and additional-field pair constraint
# ---------------------------------------------------------------------------


class TestInpsRatesIvsAndAdditional:
    """InpsRates validators: IVS <= total and paired additional fields."""

    _BASE: dict[str, Any] = {
        "employee_rate": "0.0919",
        "employee_ivs_rate": "0.0919",
        "employer_rate": "0.2898",
        "employer_ivs_rate": "0.2381",
        "ceiling": None,
    }

    def test_employee_ivs_exceeds_employee_rate_raises(self) -> None:
        """employee_ivs_rate > employee_rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="employee_ivs_rate"):
            InpsRates(**{**self._BASE, "employee_ivs_rate": "0.30"})

    def test_employer_ivs_exceeds_employer_rate_raises(self) -> None:
        """employer_ivs_rate > employer_rate must raise ValidationError."""
        with pytest.raises(ValidationError, match="employer_ivs_rate"):
            InpsRates(**{**self._BASE, "employer_ivs_rate": "0.40"})

    def test_additional_rate_without_threshold_raises(self) -> None:
        """employee_additional_rate set without threshold must raise."""
        with pytest.raises(ValidationError, match="both be set or both be absent"):
            InpsRates(**{
                **self._BASE,
                "employee_additional_rate": "0.01",
            })

    def test_additional_threshold_without_rate_raises(self) -> None:
        """employee_additional_threshold set without rate must raise."""
        with pytest.raises(ValidationError, match="both be set or both be absent"):
            InpsRates(**{
                **self._BASE,
                "employee_additional_threshold": "56224",
            })

    def test_negative_additional_threshold_raises(self) -> None:
        """employee_additional_threshold < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRates(**{
                **self._BASE,
                "employee_additional_rate": "0.01",
                "employee_additional_threshold": "-1000",
            })

    def test_valid_with_additional_fields(self) -> None:
        """Valid rate+threshold pair is accepted."""
        r = InpsRates(**{
            **self._BASE,
            "employee_additional_rate": "0.01",
            "employee_additional_threshold": "56224",
        })
        assert r.employee_additional_rate == Decimal("0.01")
        assert r.employee_additional_threshold == Decimal(56224)


# ---------------------------------------------------------------------------
# InpsRawRates: negative additional_threshold
# ---------------------------------------------------------------------------


class TestInpsRawRatesAdditionalThreshold:
    """InpsRawRates rejects a negative employee_additional_threshold."""

    _TIER: dict[str, Any] = {
        "max_employees": None,
        "rate": "0.0919",
        "ivs_rate": "0.0919",
    }

    def test_negative_threshold_raises(self) -> None:
        """employee_additional_threshold < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            InpsRawRates(
                employee_tiers=[InpsEmployeeTier.model_validate(self._TIER)],
                employer_tiers=[
                    InpsEmployerTier.model_validate({
                        **self._TIER,
                        "rate": "0.2898",
                        "ivs_rate": "0.2381",
                    })
                ],
                ceiling=None,
                employee_additional_rate=Decimal("0.01"),
                employee_additional_threshold=Decimal(-1000),
            )

    def test_zero_threshold_accepted(self) -> None:
        """employee_additional_threshold = 0 is on the boundary and accepted."""
        raw = InpsRawRates(
            employee_tiers=[InpsEmployeeTier.model_validate(self._TIER)],
            employer_tiers=[
                InpsEmployerTier.model_validate({
                    **self._TIER,
                    "rate": "0.2898",
                    "ivs_rate": "0.2381",
                })
            ],
            ceiling=None,
            employee_additional_rate=Decimal("0.01"),
            employee_additional_threshold=Decimal(0),
        )
        assert raw.employee_additional_threshold == Decimal(0)


# ---------------------------------------------------------------------------
# SommaEsenteRules: band validation
# ---------------------------------------------------------------------------


_VALID_BAND_LIST: list[SommaEsenteBand] = [
    SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071")),
    SommaEsenteBand(up_to=Decimal(15000), rate=Decimal("0.053")),
    SommaEsenteBand(up_to=Decimal(20000), rate=Decimal("0.048")),
]


class TestSommaEsenteBand:
    """SommaEsenteBand rejects negative and >1 rates."""

    def test_negative_rate_raises(self) -> None:
        """Rate < 0 must raise ValidationError."""
        with pytest.raises(ValidationError):
            SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("-0.05"))

    def test_rate_above_one_raises(self) -> None:
        """Rate > 1 must raise ValidationError."""
        with pytest.raises(ValidationError):
            SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("1.5"))

    def test_valid_band_accepted(self) -> None:
        """Valid rate in [0, 1] is accepted."""
        b = SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071"))
        assert b.rate == Decimal("0.071")


class TestSommaEsenteRules:
    """SommaEsenteRules: empty, duplicate, non-ascending bands are rejected."""

    def test_empty_bands_raises(self) -> None:
        """Empty bands list must raise ValidationError."""
        with pytest.raises(ValidationError):
            SommaEsenteRules(bands=[])

    def test_non_ascending_bands_raises(self) -> None:
        """Bands with non-ascending up_to must raise ValidationError."""
        with pytest.raises(ValidationError, match="strictly ascending"):
            SommaEsenteRules(
                bands=[
                    SommaEsenteBand(up_to=Decimal(15000), rate=Decimal("0.053")),
                    SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071")),
                ]
            )

    def test_duplicate_up_to_raises(self) -> None:
        """Bands with equal up_to must raise ValidationError."""
        with pytest.raises(ValidationError, match="strictly ascending"):
            SommaEsenteRules(
                bands=[
                    SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.071")),
                    SommaEsenteBand(up_to=Decimal(8500), rate=Decimal("0.053")),
                ]
            )

    def test_single_band_accepted(self) -> None:
        """A single band (no ordering to check) is accepted."""
        r = SommaEsenteRules(
            bands=[SommaEsenteBand(up_to=Decimal(20000), rate=Decimal("0.05"))]
        )
        assert len(r.bands) == 1

    def test_valid_bands_accepted(self) -> None:
        """Three strictly-ascending bands are accepted."""
        r = SommaEsenteRules(bands=_VALID_BAND_LIST)
        assert len(r.bands) == 3


# ---------------------------------------------------------------------------
# fixed_term_additional_rate: PercentageRate constraint
# ---------------------------------------------------------------------------


class TestFixedTermAdditionalRate:
    """YearRulesRaw and YearRules reject negative / >1 fixed_term_additional_rate."""

    def test_negative_rate_in_year_rules_raises(self) -> None:
        """Negative fixed_term_additional_rate must raise ValidationError."""
        with pytest.raises(ValidationError):
            YearRules.model_validate(
                _year_rules({"fixed_term_additional_rate": "-0.01"})
            )

    def test_rate_above_one_in_year_rules_raises(self) -> None:
        """fixed_term_additional_rate > 1 must raise ValidationError."""
        with pytest.raises(ValidationError):
            YearRules.model_validate(_year_rules({"fixed_term_additional_rate": "1.5"}))

    def test_zero_rate_accepted(self) -> None:
        """fixed_term_additional_rate = 0 (PA sector) must be accepted."""
        r = YearRules.model_validate(
            _year_rules({"fixed_term_additional_rate": "0.000"})
        )
        assert r.fixed_term_additional_rate == Decimal(0)
