"""Scatti of ABI, operai agricoli and artisan metalworkers from the full texts.

- ABI, testo coordinato of the CCNL of 23 November 2023 (FABI, sha256
  4d92bc5226736682ddb1eedfaf7940df989fdc3cbbd99d0fa6347fd91979a933, Art. 94
  and 103): first scatto after 4 years, then every 3, at most 8, 7 for QD3
  and QD4.
- Operai agricoli, CCNL 23 May 2022 (FLAI, sha256
  49ae5803f2081985a0e1a10f64e9019e1b999e808da9d3681eaab24c3dee674c, Art.
  54): every two years, at most 5.
- Area meccanica artigianato, EBNA text (sha256
  f8cd3c42582324aa4484bb2bb9465a5a0a442467aae64e3ea3a1c57e089f3151, Art. 60
  and 71): every two years, at most 5, fixed amounts.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl


def test_abi_cadence_and_maxima() -> None:
    """48 months, then 36; 8 scatti, 7 for QD3 and QD4."""
    si = load_ccnl("bancari-abi.json").parameters.seniority_increments

    assert (si.first_cadence_months, si.cadence_months) == (48, 36)
    assert si.maximum_count == 8
    assert dict(si.maximum_count_by_level) == {"QD3": 7, "QD4": 7}


def test_operai_agricoli_scatti_are_biennial() -> None:
    """Art. 54: 'per ciascun biennio di anzianità'."""
    si = load_ccnl("operai-agricoli-florovivaisti.json").parameters.seniority_increments

    assert (si.cadence_months, si.maximum_count) == (24, 5)


def test_artisan_scatti_amounts() -> None:
    """The fixed amounts for the workers hired after 27 November 1997."""
    ccnl = load_ccnl("metalmeccanico-artigianato.json")
    si = ccnl.parameters.seniority_increments
    amounts = {
        level: series.periods[-1].value for level, series in si.amount_by_level.items()
    }

    assert (si.cadence_months, si.maximum_count) == (24, 5)
    assert amounts == {
        level: Decimal(value)
        for level, value in {
            "1Q": "32.94",
            "1": "32.94",
            "2": "29.08",
            "2bis": "26.13",
            "3": "24.29",
            "4": "21.72",
            "5": "20.24",
            "6": "18.40",
        }.items()
    }
