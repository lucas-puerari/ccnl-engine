"""YearRules validators and the bundled 2026 tax rules loaded by load_year_rules.

The rate and band models YearRules is built from are tested in
``tests/unit/ccnl_engine/tax/domain/``.
"""

from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.shared.domain.errors import DataIntegrityError
from ccnl_engine.tax.domain.contribution_tiers import (
    InpsEmployeeTier,
)
from ccnl_engine.tax.domain.ruleset import YearRules, YearRulesRaw
from ccnl_engine.tax.domain.tfr_rules import TfrRules
from ccnl_engine.tax.service.tax_annual_assembler import load_year_rules
from ccnl_engine.tax.service.tax_resource_reader import (
    read_inps_rules_raw,
    read_tax_rules_raw,
)
from ccnl_engine.tax.service.tax_tier_resolver import (
    _assert_tier_integrity,
    _resolve_tier,
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


_RAW_BASE: dict[str, Any] = {
    "year": 2026,
    "sector": "terziario",
    "irpef_brackets": IRPEF_BRACKETS_2026,
    "fixed_term_additional_rate": "0.014",
    "tfr": {"accrual_divisor": "13.5"},
}


class TestYearRulesRawContributionModel:
    """YearRulesRaw validator: must have inps+apprentice or domestic_contributions."""

    def test_missing_both_raises(self) -> None:
        """Neither inps+apprentice nor domestic_contributions → ValidationError."""
        with pytest.raises(ValidationError, match="domestic_contributions"):
            YearRulesRaw.model_validate(_RAW_BASE)

    def test_both_models_raises(self) -> None:
        """Having both standard and domestic models is rejected."""
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
