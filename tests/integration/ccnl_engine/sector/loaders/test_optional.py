"""Unit tests for tax loaders — year-mismatch guard in load_variable_pay_rules."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.errors import DataIntegrityError, UnsupportedTaxYearError
from ccnl_engine.family.loaders import load_family_deduction_rules
from ccnl_engine.sector.loaders import (
    _assembled,
    _clear_year_rules,
    load_year_rules,
)
from ccnl_engine.sector.models import YearRulesRaw
from ccnl_engine.sector.raw.loaders import _try_ruleset
from ccnl_engine.severance.loaders import load_tfr_revaluation_rules
from ccnl_engine.variable_pay.loaders import load_variable_pay_rules

if TYPE_CHECKING:
    from collections.abc import Iterator

_CACHED = (
    load_family_deduction_rules,
    load_tfr_revaluation_rules,
    load_variable_pay_rules,
)


@pytest.fixture(autouse=True)
def _fresh_loaders() -> Iterator[None]:
    """Clear the loader caches, so a patched reader is read again."""
    for loader in _CACHED:
        loader.cache_clear()
    yield
    for loader in _CACHED:
        loader.cache_clear()


def test_year_keyed_rules_of_unbundled_year_raise_domain_error() -> None:
    """A year the bundle does not ship raises UnsupportedTaxYearError."""
    with pytest.raises(UnsupportedTaxYearError) as info:
        load_family_deduction_rules(1900)
    assert info.value.year == 1900
    assert info.value.sector is None


class TestLoadVariablePayRules:
    """load_variable_pay_rules validation."""

    def test_correct_year_loads_successfully(self) -> None:
        """Requesting the bundled year returns a VariablePayRules instance."""
        rules = load_variable_pay_rules(2026)
        assert rules.year == 2026

    def test_unbundled_year_raises(self) -> None:
        """A year without a variable-pay-rules file is not supported."""
        with pytest.raises(UnsupportedTaxYearError):
            load_variable_pay_rules(2099)

    def test_wrong_year_raises(self) -> None:
        """A file whose year does not match its name is rejected."""
        with (
            patch(
                "ccnl_engine.variable_pay.loaders.read_year_json",
                return_value={"year": 2026},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_variable_pay_rules(2027)


class TestLoadTfrRevaluationRules:
    """load_tfr_revaluation_rules: the bundled 2026 file and its checks."""

    def test_2026_rules_carry_the_istat_indexes_and_the_tax(self) -> None:
        """The values of art. 2120 c. 4 c.c., ISTAT and D.Lgs. 47/2000.

        1,5 and 75 per cento (art. 2120 c. 4 c.c.); FOI without tobacco of
        December 2025, 121,5 base 2015=100, and link coefficient 1,214 to
        base 2025 (ISTAT serie08_2026.xlsx, Tabella 10); December 2026 not
        published on 7 October 2026; 17 per cento (D.Lgs. 47/2000 art. 11
        c. 3, text in force until 31-12-2026).
        """
        rules = load_tfr_revaluation_rules(2026)
        assert rules is not None
        assert (rules.rate.fixed, rules.rate.index_share) == (
            Decimal("0.015"),
            Decimal("0.75"),
        )
        index = rules.price_index
        assert index.previous_december == Decimal("121.5")
        assert index.link_coefficient == Decimal("1.214")
        assert index.december is None
        assert rules.substitute_tax.rate == Decimal("0.17")
        assert rules.ruleset is not None
        assert rules.ruleset.id == "tax/2026/tfr-revaluation"

    def test_unbundled_year_has_no_rules(self) -> None:
        """No file for 2027: the revaluation of that year has no rules."""
        assert load_tfr_revaluation_rules(2027) is None

    def test_invalid_table_raises(self) -> None:
        """A table that does not validate is a data integrity error."""
        with (
            patch(
                "ccnl_engine.severance.loaders.read_year_json",
                return_value={"year": 2026, "rate": {}},
            ),
            pytest.raises(DataIntegrityError, match="not a valid TFR revaluation"),
        ):
            load_tfr_revaluation_rules(2026)

    def test_year_mismatch_raises(self) -> None:
        """A file of another year under the 2026 name is rejected."""
        rules = load_tfr_revaluation_rules(2026)
        assert rules is not None
        raw = rules.model_dump(mode="json", exclude={"ruleset"}) | {"year": 2025}
        load_tfr_revaluation_rules.cache_clear()
        with (
            patch(
                "ccnl_engine.severance.loaders.read_year_json",
                return_value=raw,
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_tfr_revaluation_rules(2026)


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
        """A tampered file where year != filename year raises."""
        tampered_raw = {"year": 9999, "description": "tampered"}
        with (
            patch(
                "ccnl_engine.family.loaders.read_year_json",
                return_value=tampered_raw,
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_family_deduction_rules(2026)

    def test_invalid_table_raises(self) -> None:
        """A table that does not validate is a data integrity error."""
        with (
            patch(
                "ccnl_engine.family.loaders.read_year_json",
                return_value={"year": 2026, "spouse": {}},
            ),
            pytest.raises(DataIntegrityError, match="not a valid family deduction"),
        ):
            load_family_deduction_rules(2026)

    def test_spouse_increases_are_the_five_bands_of_lett_b(self) -> None:
        """Art. 12 c. 1 lett. b, read on Normattiva on 3 October 2026."""
        bands = load_family_deduction_rules(2026).spouse_increases.bands
        assert [(b.above, b.up_to, b.amount) for b in bands] == [
            (Decimal(29000), Decimal(29200), Decimal(10)),
            (Decimal(29200), Decimal(34700), Decimal(20)),
            (Decimal(34700), Decimal(35000), Decimal(30)),
            (Decimal(35000), Decimal(35100), Decimal(20)),
            (Decimal(35100), Decimal(35200), Decimal(10)),
        ]


class TestTryRuleset:
    """_try_ruleset returns None gracefully for non-dict ruleset values."""

    def test_non_dict_ruleset_returns_none(self) -> None:
        """A non-dict ruleset value (e.g. a string) returns None."""
        assert _try_ruleset({"ruleset": "not-a-dict"}) is None

    def test_missing_ruleset_key_returns_none(self) -> None:
        """A payload without a ruleset key returns None."""
        assert _try_ruleset({"year": 2026}) is None


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
    "fixed_term_renewal_increment": "0.005",
    "tfr": {"accrual_divisor": "13.5"},
}


class TestResolveInpsAdditionalValidation:
    """The loader rejects an additional 1% IVS block that cannot hold."""

    def test_monthly_threshold_above_the_annual_raises(self) -> None:
        """A monthly threshold above the annual one fails at load time."""
        bad_inps = {
            "employee_tiers": [
                {"max_employees": None, "rate": "0.0949", "ivs_rate": "0.0949"}
            ],
            "employer_tiers": [
                {"max_employees": None, "rate": "0.3050", "ivs_rate": "0.2381"}
            ],
            "ceiling": "122295.00",
            "employee_additional": {
                "rate": "0.01",
                "annual_threshold": "4685.00",
                "monthly_threshold": "56224.00",
            },
        }
        bad_inps_raw = {
            "year": 2026,
            "sector": "industria",
            "inps": bad_inps,
            "apprentice": _BAD_APPRENTICE,
        }
        _clear_year_rules()
        with (
            patch(
                "ccnl_engine.sector.loaders.read_tax_rules_raw",
                return_value=_BAD_TAX_RAW,
            ),
            patch(
                "ccnl_engine.sector.loaders.read_inps_rules_raw",
                return_value=bad_inps_raw,
            ),
            pytest.raises(ValidationError, match="must not exceed"),
        ):
            load_year_rules(2026, TaxSector.INDUSTRIA, 100)
        _clear_year_rules()


class TestLoadYearRulesIdentity:
    """The year rules reject mismatched year/sector in tax and INPS files."""

    def test_tax_year_mismatch_raises(self) -> None:
        """Tax file with wrong year raises ValueError before merge."""
        _clear_year_rules()
        with (
            patch(
                "ccnl_engine.sector.loaders.read_tax_rules_raw",
                return_value={"year": 9999, "sector": "terziario"},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _clear_year_rules()

    def test_tax_sector_mismatch_raises(self) -> None:
        """Tax file with wrong sector raises ValueError before merge."""
        _clear_year_rules()
        with (
            patch(
                "ccnl_engine.sector.loaders.read_tax_rules_raw",
                return_value={"year": 2026, "sector": "invalid"},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested sector"),
        ):
            load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _clear_year_rules()

    def test_inps_year_mismatch_raises(self) -> None:
        """INPS file with wrong year raises ValueError before merge."""
        _clear_year_rules()
        with (
            patch(
                "ccnl_engine.sector.loaders.read_tax_rules_raw",
                return_value={"year": 2026, "sector": "terziario"},
            ),
            patch(
                "ccnl_engine.sector.loaders.read_inps_rules_raw",
                return_value={"year": 9999, "sector": "terziario"},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested year"),
        ):
            load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _clear_year_rules()

    def test_inps_sector_mismatch_raises(self) -> None:
        """INPS file with wrong sector raises ValueError before merge."""
        _clear_year_rules()
        with (
            patch(
                "ccnl_engine.sector.loaders.read_tax_rules_raw",
                return_value={"year": 2026, "sector": "terziario"},
            ),
            patch(
                "ccnl_engine.sector.loaders.read_inps_rules_raw",
                return_value={"year": 2026, "sector": "invalid"},
            ),
            pytest.raises(DataIntegrityError, match="does not match requested sector"),
        ):
            load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _clear_year_rules()


class TestWorkDeductionPassthrough:
    """load_year_rules reads work_deduction from the one file of the year."""

    def test_default_work_deduction_detr_flat(self) -> None:
        """The loaded 2026 terziario rules carry detr_flat = 1955 from JSON."""
        _clear_year_rules()
        rules = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        _clear_year_rules()
        assert rules.work_deduction.detr_flat == Decimal(1955)

    def test_a_sector_file_cannot_restate_the_constants(self) -> None:
        """The constants live in one file per year: a sector file stating them fails."""
        restated = {**_BAD_TAX_RAW, "work_deduction": {"detr_flat": "9999"}}
        with pytest.raises(ValidationError, match="work_deduction"):
            YearRulesRaw.model_validate(restated)

    def test_all_2026_sectors_have_explicit_work_deduction(self) -> None:
        """Every standard sector reads detr_flat = 1955 from the year file."""
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
            _clear_year_rules()
            rules = load_year_rules(2026, sector, 50)
            assert rules.work_deduction.detr_flat == Decimal(1955), (
                f"sector {sector.value}: detr_flat mismatch"
            )
        _clear_year_rules()

    def test_lavoro_domestico_has_explicit_work_deduction(self) -> None:
        """Lavoro domestico reads detr_flat = 1955 from the year file."""
        _clear_year_rules()
        rules = load_year_rules(2026, TaxSector.LAVORO_DOMESTICO, 1)
        _clear_year_rules()
        assert rules.work_deduction.detr_flat == Decimal(1955)


def test_the_cache_holds_one_entry_per_tier_not_per_headcount() -> None:
    """200 headcounts of the same tiers share a handful of year rules."""
    _clear_year_rules()
    for headcount in range(1, 201):
        load_year_rules(2026, TaxSector.TERZIARIO, headcount)
    assert _assembled.cache_info().currsize <= 5
    assert load_year_rules(2026, TaxSector.TERZIARIO, 120) is load_year_rules(
        2026, TaxSector.TERZIARIO, 180
    )
    _clear_year_rules()
