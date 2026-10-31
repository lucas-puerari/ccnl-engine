"""Sickness rules of ABI and the artisan metalworkers from the full texts.

- ABI, testo coordinato of 23 November 2023 (FABI, sha256
  4d92bc5226736682ddb1eedfaf7940df989fdc3cbbd99d0fa6347fd91979a933), Art. 66
  c. 1: the job and the whole pay for 6 to 22 months of one illness, by
  seniority (the 48 months of c. 2 are an option of the bank).
- Area meccanica artigianato, EBNA text (sha256
  f8cd3c42582324aa4484bb2bb9465a5a0a442467aae64e3ea3a1c57e089f3151), Art.
  61: top-up to 100% of the net pay from the fourth day, from the first past
  7 days, for at most 150 days.
- Ortofrutticoli (FLAI text of 19 July 2024, sha256
  0264d1857a1f61cf0ff2e4028e78cb6e7d5c74ca133b765acef993dd2edfa38e), Art.
  22: 100% carenza, 75% days 4-20, 100% days 21-180.
- Consorzi di bonifica (21 May 2025, sha256
  8f09770620642bc2d3179029ddacf84f7f5530831c5d5d5d6f854f2fb955c83a), Art.
  98: the whole pay for 10 months, half for 5 more.
- Area Tessile-Moda artigianato (16 July 2024, sha256
  a42631366ff40865c48517ad61ee7b93002a1a938945946741cff3161d30f310), Art.
  109: operai 80% days 1-7, 100% net days 8-180; Art. 97: 12 months.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl


def test_abi_bands_by_seniority() -> None:
    """Six bands of one illness, 30-day months, no window."""
    rules = load_ccnl("bancari-abi").work_rules
    assert rules is not None
    sickness = rules.sickness_rules
    assert sickness is not None
    assert sickness.cumulation is None
    assert not sickness.comporto_windows

    assert [b.comporto_days for b in sickness.comporto_bands] == [
        180,
        240,
        360,
        450,
        540,
        660,
    ]


@pytest.mark.parametrize(
    ("slug", "carenza", "rates", "comporto"),
    [
        ("ortofrutticoli-agrumari", "1", [(4, 21, "0.75"), (21, None, "1")], 180),
        ("consorzi-di-bonifica-snebi", "1", [(301, None, "0.5")], 450),
        (
            "tessile-moda-artigianato-confartigianato",
            "0.8",
            [(4, 8, "0.8"), (8, 181, "1"), (181, None, "0")],
            365,
        ),
    ],
)
def test_sick_pay_bands_from_the_texts(
    slug: str,
    carenza: str,
    rates: list[tuple[int, int | None, str]],
    comporto: int,
) -> None:
    """Day bands, or the tier of the eleventh month as days, and the comporto."""
    rules = load_ccnl(slug).work_rules
    assert rules is not None
    sickness = rules.sickness_rules
    assert sickness is not None

    stored = [(b.day_from, b.day_until, b.integration_rate) for b in sickness.day_bands]
    stored += [
        ((t.month_from - 1) * 30 + 1, t.month_until, t.integration_rate)
        for t in sickness.tiers
    ]
    assert stored == [(a, b, Decimal(r)) for a, b, r in rates]
    assert sickness.carenza_integration_rate == Decimal(carenza)
    assert sickness.max_duration_days == comporto


def test_artisan_operai_sickness() -> None:
    """Net 100%, carenza only past 7 days, 150 days; 9 months, 10 in 24."""
    rules = load_ccnl("metalmeccanico-artigianato").work_rules
    assert rules is not None
    sickness = rules.sickness_rules
    assert sickness is not None

    assert sickness.full_pay_integration_rate == Decimal(1)
    assert sickness.net_basis is True
    assert sickness.carenza_min_days == 7
    assert sickness.max_duration_days == 274
    assert [t.month_from for t in sickness.tiers] == [6]
    assert sickness.tiers[0].integration_rate == 0
    (window,) = sickness.comporto_windows
    assert (window.window_months, window.comporto_days) == (24, 304)


def test_domestic_sickness_bands() -> None:
    """Art. 27 of the CCNL of 28 October 2025: 8/10, 10/45, 15/180 days."""
    rules = load_ccnl("lavoro-domestico-non-convivente").work_rules
    assert rules is not None
    sickness = rules.sickness_rules
    assert sickness is not None
    assert sickness.cumulation is not None

    assert sickness.carenza_integration_rate == Decimal("0.5")
    assert [(b.full_pay_days, b.comporto_days) for b in sickness.cumulation.bands] == [
        (8, 10),
        (10, 45),
        (15, 180),
    ]
