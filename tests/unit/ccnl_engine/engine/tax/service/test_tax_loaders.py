"""Unit tests for tax loaders — year-mismatch guard in load_variable_pay_rules."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.tax.service.loaders import load_variable_pay_rules


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
