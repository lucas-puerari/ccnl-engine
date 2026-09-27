"""Bundled sick-pay rates load through the optional tax loaders."""

from __future__ import annotations

from ccnl_engine.tax.service.tax_optional_loaders import load_sick_pay_rates


class TestMiscCoverageGaps:
    """Bundled sick-pay rates."""

    def test_load_sick_pay_rates_returns_valid_rates(self) -> None:
        """load_sick_pay_rates() loads the bundled sick-pay JSON without error."""
        rates = load_sick_pay_rates()
        assert rates.carenza_days >= 0
