"""Bundled sick-pay rates load through the optional tax loaders."""

from __future__ import annotations

from ccnl_engine.provenance.domain.chain import ProvenanceStatus
from ccnl_engine.tax.service.tax_optional_loaders import load_sick_pay_rates


class TestMiscCoverageGaps:
    """Bundled sick-pay rates."""

    def test_load_sick_pay_rates_returns_valid_rates(self) -> None:
        """load_sick_pay_rates() loads the bundled sick-pay JSON without error."""
        rates = load_sick_pay_rates()
        assert rates.carenza_days >= 0

    def test_indemnity_bands_carry_their_provenance_record(self) -> None:
        """The bands record is read from ``bands_provenance``, never left empty."""
        record = load_sick_pay_rates().bands_provenance
        assert record is not None
        assert record.status is ProvenanceStatus.DERIVED
        assert record.location is not None
