"""Sickness rules of ABI and the artisan metalworkers from the full texts.

- ABI, testo coordinato of 23 November 2023 (FABI, sha256
  4d92bc5226736682ddb1eedfaf7940df989fdc3cbbd99d0fa6347fd91979a933), Art. 66
  c. 2: the whole pay for 8 to 24 months of sickness in 48 months, by
  seniority.
- Area meccanica artigianato, EBNA text (sha256
  f8cd3c42582324aa4484bb2bb9465a5a0a442467aae64e3ea3a1c57e089f3151), Art.
  61: top-up to 100% of the net pay from the fourth day, from the first past
  7 days, for at most 150 days.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl


def test_abi_bands_by_seniority() -> None:
    """Six bands over a four-year window, 30-day months."""
    rules = load_ccnl("bancari-abi.json").work_rules
    assert rules is not None
    sickness = rules.sickness_rules
    assert sickness is not None
    assert sickness.cumulation is not None

    assert sickness.cumulation.window_years == 4
    assert [b.full_pay_days for b in sickness.cumulation.bands] == [
        240,
        300,
        420,
        540,
        660,
        720,
    ]
    assert sickness.cumulation.band_of(130).comporto_days == 420


def test_artisan_operai_sickness() -> None:
    """Net 100%, carenza only past 7 days, 150 days."""
    rules = load_ccnl("metalmeccanico-artigianato.json").work_rules
    assert rules is not None
    sickness = rules.sickness_rules
    assert sickness is not None

    assert sickness.full_pay_integration_rate == Decimal(1)
    assert sickness.net_basis is True
    assert sickness.carenza_min_days == 7
    assert sickness.max_duration_days == 150
