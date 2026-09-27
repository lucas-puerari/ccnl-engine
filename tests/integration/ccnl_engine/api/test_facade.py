"""PayrollEngine construction from the bundled knowledge."""

from __future__ import annotations

from ccnl_engine.api.facade import PayrollEngine


class TestMiscCoverageGaps:
    """Bundled engine construction."""

    def test_payroll_engine_bundled(self) -> None:
        """PayrollEngine.bundled() returns a live engine instance."""
        engine = PayrollEngine.bundled()
        assert engine is not None
