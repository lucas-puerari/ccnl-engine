"""Rule cited when a household employer skips the payroll taxes."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.withholding.rules_agent import (
    NOT_WITHHOLDING_AGENT,
    not_withholding_agent_decision,
)


@pytest.mark.parametrize(
    ("tax_year", "rule", "section"),
    [
        (2026, "dpr600-1973-art23-c1", "art. 23 c. 1"),
        (2027, "dlgs33-2025-art33-c1", "art. 33 c. 1"),
    ],
)
def test_rule_follows_the_norm_in_force(tax_year: int, rule: str, section: str) -> None:
    """Art. 23 D.P.R. 600/1973 until 2026, art. 33 D.Lgs. 33/2025 from 2027."""
    decision = not_withholding_agent_decision("irpef", tax_year)

    assert decision.rule == rule
    assert decision.rule_version == str(tax_year)
    assert decision.source is not None
    assert decision.source.section == section
    assert decision.reason_code == NOT_WITHHOLDING_AGENT
    assert decision.status is CalculationStatus.FINAL
    assert decision.amount == Decimal(0)
