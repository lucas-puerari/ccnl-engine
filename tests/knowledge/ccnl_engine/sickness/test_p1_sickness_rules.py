"""Leave and sickness rules of the first-round CCNLs read from their texts.

Sanità privata, CCNL of 8 October 2020 (sha256
183c5c0a01c9a113fd08efffed8132b4e598e4db574f6aed402afb7be880a442): Art. 43
(pp. 58-60) tops sickness up to 100% of the retribuzione globale, net of what
the worker would have received, up to the 365th day of absence in four years,
within a comporto of 540 days in a rolling four years; Art. 32 (p. 42) gives
30 working days of ferie plus 4 for the festività soppresse.  Operai agricoli,
verbale of 28 May 2026 (sha256
487f3412d7fdb68c80b4d7e5cff223888c34ce51fc109b6a9ebdecda689dd6fa): 26 days of
ferie (Art. 36), 180 days of comporto (Art. 61), the florovivaisti
integration of Art. 62 declared.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.catalog.loaders import load_ccnl

if TYPE_CHECKING:
    from ccnl_engine.agreement.coverage.models import CCNLWorkRules


def _rules(slug: str) -> CCNLWorkRules:
    rules = load_ccnl(slug).work_rules
    assert rules is not None
    return rules


def test_sanita_privata_sickness_is_paid_in_full_for_a_year_in_four() -> None:
    """100% net from the first day, 365 days in four years, comporto 540."""
    sickness = _rules("sanita-privata-aiop-aris").sickness_rules
    assert sickness is not None
    assert sickness.cumulation is not None
    band = sickness.cumulation.band_of(0)

    assert sickness.carenza_integration_rate == Decimal(1)
    assert sickness.full_pay_integration_rate == Decimal(1)
    assert sickness.net_basis is True
    assert sickness.cumulation.window_years == 4
    assert (band.full_pay_days, band.comporto_days) == (365, 540)
    assert sickness.cumulation.reduced_integration_rate == Decimal(0)


def test_sanita_privata_ferie_include_the_festivita_soppresse() -> None:
    """30 working days plus 4."""
    leave = _rules("sanita-privata-aiop-aris").leave_rules
    assert leave is not None

    assert leave.default_annual_days == Decimal(34)


def test_operai_agricoli_leave_and_comporto() -> None:
    """26 days of ferie, 180 days of comporto, no employer integration."""
    rules = _rules("operai-agricoli-florovivaisti")
    assert rules.leave_rules is not None
    assert rules.sickness_rules is not None
    ccnl = load_ccnl("operai-agricoli-florovivaisti")
    variants = {n.limitation.variant for n in ccnl.coverage.notes if n.limitation}

    assert rules.leave_rules.default_annual_days == Decimal(26)
    assert rules.sickness_rules.max_duration_days == 180
    assert rules.sickness_rules.full_pay_integration_rate == Decimal(0)
    assert "florovivaisti_sickness_integration" in variants
