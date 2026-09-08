"""Unit tests for tax loaders — year-mismatch guard in load_variable_pay_rules."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from ccnl_engine.engine.tax.service.loaders import (
    load_art15_deduction_rules,
    load_family_deduction_rules,
    load_variable_pay_rules,
)


class TestLoadVariablePayRules:
    """load_variable_pay_rules validation."""

    def test_correct_year_loads_successfully(self) -> None:
        """Requesting the bundled year returns a VariablePayRules instance."""
        rules = load_variable_pay_rules(2026)
        assert rules.year == 2026

    def test_wrong_year_raises(self) -> None:
        """Requesting a year that does not match the file raises ValueError."""
        with pytest.raises(ValueError, match="does not match requested year"):
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
                "disabled_amount": "1220.00",
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
                "ccnl_engine.engine.tax.service.loaders._read_json",
                return_value=tampered_raw,
            ),
            pytest.raises(ValueError, match="does not match requested year"),
        ):
            load_family_deduction_rules(2026)


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
                "ccnl_engine.engine.tax.service.loaders._read_json",
                return_value=tampered_raw,
            ),
            pytest.raises(ValueError, match="does not match requested year"),
        ):
            load_art15_deduction_rules(2026)
