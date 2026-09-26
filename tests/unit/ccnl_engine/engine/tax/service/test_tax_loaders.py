"""Unit tests for tax loaders — year-mismatch guard in load_variable_pay_rules."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from ccnl_engine.engine.contract.domain.ccnl import TaxSector
from ccnl_engine.engine.errors import DataIntegrityError, UnsupportedTaxYearError
from ccnl_engine.engine.tax.service.loaders import (
    _load_year_rules_cached,
    _try_ruleset,
    load_art15_deduction_rules,
    load_family_deduction_rules,
    load_variable_pay_rules,
    load_year_rules,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.parametrize(
    "loader", [load_family_deduction_rules, load_art15_deduction_rules]
)
def test_year_keyed_rules_of_unbundled_year_raise_domain_error(
    loader: Callable[[int], object],
) -> None:
    """A year the bundle does not ship raises UnsupportedTaxYearError."""
    with pytest.raises(UnsupportedTaxYearError) as info:
        loader(1900)
    assert info.value.year == 1900
    assert info.value.sector is None


class TestLoadVariablePayRules:
    """load_variable_pay_rules validation."""

    def test_correct_year_loads_successfully(self) -> None:
        """Requesting the bundled year returns a VariablePayRules instance."""
        rules = load_variable_pay_rules(2026)
        assert rules.year == 2026

    def test_wrong_year_raises(self) -> None:
        """Requesting a year that does not match the file raises ValueError."""
        with pytest.raises(DataIntegrityError, match="does not match requested year"):
            load_variable_pay_rules(2099)


class TestLoadFamilyDeductionRules:
    """load_family_deduction_rules validation."""

    def test_correct_year_loads_successfully(self) -> None:
        """Requesting the bundled 2026 year returns a FamilyDeductionRules."""
        rules = load_family_deduction_rules(2026)
        assert rules.year == 2026
        assert rules.spouse.dependent_income_threshold > 0
        assert rules.children.base_amount > 0
        assert rules.other_dependents.amount > 0

    def test_year_mismatch_raises(self) -> None:
        """A tampered file where year != filename year raises ValueError."""
        # Simulate a hand-edited JSON where the year field was changed.
        tampered_raw = {
            "year": 9999,
            "description": "tampered",
            "spouse": {
                "dependent_income_threshold": "2840.51",
                "breakpoints": [
                    {"income_up_to": None, "deduction": "0.00"},
                ],
                "notes": "",
            },
            "children": {
                "auu_age_cutoff": 21,
                "base_amount": "950.00",
                "income_ceiling": "95000.00",
                "income_ceiling_increment_per_child": "15000.00",
                "notes": "",
            },
            "other_dependents": {
                "dependent_income_threshold": "2840.51",
                "amount": "750.00",
                "income_ceiling": "80000.00",
                "notes": "",
            },
        }
        with (
            patch(
                "ccnl_engine.engine.tax.service.tax_optional_loaders.read_year_json",
                return_value=tampered_raw,
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_family_deduction_rules(2026)


class TestTryRuleset:
    """_try_ruleset returns None gracefully for non-dict ruleset values."""

    def test_non_dict_ruleset_returns_none(self) -> None:
        """A non-dict ruleset value (e.g. a string) returns None."""
        assert _try_ruleset({"ruleset": "not-a-dict"}) is None

    def test_missing_ruleset_key_returns_none(self) -> None:
        """A payload without a ruleset key returns None."""
        assert _try_ruleset({"year": 2026}) is None


class TestLoadArt15DeductionRules:
    """load_art15_deduction_rules validation."""

    def test_correct_year_loads_successfully(self) -> None:
        """Requesting the bundled 2026 year returns an Art15DeductionRules."""
        rules = load_art15_deduction_rules(2026)
        assert rules.year == 2026
        assert rules.mortgage_interest.ceiling > 0
        assert rules.mortgage_interest.rate > 0

    def test_year_mismatch_raises(self) -> None:
        """A tampered file where year != filename year raises ValueError."""
        tampered_raw = {
            "year": 9999,
            "description": "tampered",
            "mortgage_interest": {
                "ceiling": "4000.00",
                "rate": "0.19",
                "notes": "",
            },
        }
        with (
            patch(
                "ccnl_engine.engine.tax.service.tax_optional_loaders.read_year_json",
                return_value=tampered_raw,
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_art15_deduction_rules(2026)


_BAD_APPRENTICE = {
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

_BAD_TAX_RAW = {
    "year": 2026,
    "sector": "industria",
    "irpef_brackets": [{"up_to": None, "rate": "0.43"}],
    "fixed_term_additional_rate": "0.014",
    "tfr": {"accrual_divisor": "13.5"},
}


class TestResolveInpsAdditionalValidation:
    """_resolve_inps rejects partial additional-rate configuration."""

    def test_rate_without_threshold_raises(self) -> None:
        """Only employee_additional_rate set (threshold absent) raises ValueError."""
        bad_inps = {
            "employee_tiers": [
                {"max_employees": None, "rate": "0.0949", "ivs_rate": "0.0949"}
            ],
            "employer_tiers": [
                {"max_employees": None, "rate": "0.3050", "ivs_rate": "0.2381"}
            ],
            "ceiling": "122295.00",
            "employee_additional_rate": "0.01",
        }
        bad_inps_raw = {
            "year": 2026,
            "sector": "industria",
            "inps": bad_inps,
            "apprentice": _BAD_APPRENTICE,
        }
        _load_year_rules_cached.cache_clear()
        with (
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_tax_rules_raw",
                return_value=_BAD_TAX_RAW,
            ),
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_inps_rules_raw",
                return_value=bad_inps_raw,
            ),
            pytest.raises(
                DataIntegrityError, match="must both be set or both be absent"
            ),
        ):
            load_year_rules(2026, TaxSector.INDUSTRIA, 100)
        _load_year_rules_cached.cache_clear()


class TestLoadYearRulesIdentity:
    """_load_year_rules_cached rejects mismatched year/sector in tax and INPS files."""

    def test_tax_year_mismatch_raises(self) -> None:
        """Tax file with wrong year raises ValueError before merge."""
        _load_year_rules_cached.cache_clear()
        with (
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_tax_rules_raw",
                return_value={"year": 9999, "sector": "terziario"},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _load_year_rules_cached.cache_clear()

    def test_tax_sector_mismatch_raises(self) -> None:
        """Tax file with wrong sector raises ValueError before merge."""
        _load_year_rules_cached.cache_clear()
        with (
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_tax_rules_raw",
                return_value={"year": 2026, "sector": "invalid"},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested sector"),
        ):
            load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _load_year_rules_cached.cache_clear()

    def test_inps_year_mismatch_raises(self) -> None:
        """INPS file with wrong year raises ValueError before merge."""
        _load_year_rules_cached.cache_clear()
        with (
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_tax_rules_raw",
                return_value={"year": 2026, "sector": "terziario"},
            ),
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_inps_rules_raw",
                return_value={"year": 9999, "sector": "terziario"},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _load_year_rules_cached.cache_clear()

    def test_inps_sector_mismatch_raises(self) -> None:
        """INPS file with wrong sector raises ValueError before merge."""
        _load_year_rules_cached.cache_clear()
        with (
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_tax_rules_raw",
                return_value={"year": 2026, "sector": "terziario"},
            ),
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_inps_rules_raw",
                return_value={"year": 2026, "sector": "invalid"},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested sector"),
        ):
            load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _load_year_rules_cached.cache_clear()


class TestWorkDeductionPassthrough:
    """load_year_rules passes work_deduction from JSON through to YearRules."""

    def test_default_work_deduction_detr_flat(self) -> None:
        """The loaded 2026 terziario rules carry detr_flat = 1955 from JSON."""
        _load_year_rules_cached.cache_clear()
        rules = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _load_year_rules_cached.cache_clear()
        assert rules.work_deduction.detr_flat == Decimal(1955)

    def test_custom_work_deduction_is_respected(self) -> None:
        """A custom work_deduction block in the tax JSON overrides the model default."""
        custom_tax_raw = dict(_BAD_TAX_RAW)
        custom_tax_raw["work_deduction"] = {
            "detr_flat": "9999",
            "detr_a": "1910",
            "detr_b_coeff": "1190",
            "detr_b_span": "13000",
            "detr_c_span": "22000",
            "detr_lo": "15000",
            "detr_mid": "28000",
            "detr_high": "50000",
            "detr_increment": "65",
            "increment_lo": "25000",
            "increment_hi": "35000",
            "seventy_five": "75",
        }
        inps_raw = {
            "year": 2026,
            "sector": "industria",
            "inps": {
                "employee_tiers": [
                    {"max_employees": None, "rate": "0.0919", "ivs_rate": "0.0919"}
                ],
                "employer_tiers": [
                    {"max_employees": None, "rate": "0.3050", "ivs_rate": "0.2381"}
                ],
                "ceiling": "122295.00",
            },
            "apprentice": _BAD_APPRENTICE,
        }
        _load_year_rules_cached.cache_clear()
        with (
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_tax_rules_raw",
                return_value=custom_tax_raw,
            ),
            patch(
                "ccnl_engine.engine.tax.service.tax_annual_assembler.read_inps_rules_raw",
                return_value=inps_raw,
            ),
        ):
            rules = load_year_rules(2026, TaxSector.INDUSTRIA, 100)
        _load_year_rules_cached.cache_clear()
        assert rules.work_deduction.detr_flat == Decimal(9999)

    def test_all_2026_sectors_have_explicit_work_deduction(self) -> None:
        """All 8 standard sectors load detr_flat = 1955 from their JSON files."""
        standard_sectors = [
            TaxSector.INDUSTRIA,
            TaxSector.TERZIARIO,
            TaxSector.CREDITO,
            TaxSector.ARTIGIANATO,
            TaxSector.AGRICOLTURA,
            TaxSector.EDILIZIA,
            TaxSector.PUBBLICA_AMMINISTRAZIONE,
        ]
        for sector in standard_sectors:
            _load_year_rules_cached.cache_clear()
            rules = load_year_rules(2026, sector, 50)
            assert rules.work_deduction.detr_flat == Decimal(1955), (
                f"sector {sector.value}: detr_flat mismatch"
            )
        _load_year_rules_cached.cache_clear()

    def test_lavoro_domestico_has_explicit_work_deduction(self) -> None:
        """Lavoro domestico sector loads detr_flat = 1955 from its JSON file."""
        _load_year_rules_cached.cache_clear()
        rules = load_year_rules(2026, TaxSector.LAVORO_DOMESTICO, 1)
        _load_year_rules_cached.cache_clear()
        assert rules.work_deduction.detr_flat == Decimal(1955)
