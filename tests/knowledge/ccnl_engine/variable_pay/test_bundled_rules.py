"""The bundled variable pay rules of 2026 against the text of the statutes.

The values of each regime are pinned to the figures of its source, so a
typo in ``knowledge/variable_pay/2026.json`` cannot pass:

- fringe benefits: L. 207/2024 art. 1 c. 390, for 2025 to 2027;
- premi di risultato: L. 199/2025 art. 1 c. 9 and L. 208/2015 art. 1 c. 186;
- renewal increments: L. 199/2025 art. 1 c. 7, for 2026 only;
- night, holiday and shift pay: L. 199/2025 art. 1 cc. 10-11, for 2026 only;
- travel allowance: TUIR art. 51 c. 5, lire at 1,936.27 per euro.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.variable_pay.loaders import load_variable_pay_rules

_RULES = load_variable_pay_rules(2026)
_LIRE_PER_EURO = Decimal("1936.27")
_CENT = Decimal("0.01")


def _euro(lire: int) -> Decimal:
    return (Decimal(lire) / _LIRE_PER_EURO).quantize(_CENT)


def test_fringe_benefit_limits() -> None:
    """1,000 EUR, 2,000 EUR for workers with dependent children."""
    fringe = _RULES.fringe_benefit

    assert (fringe.threshold_standard, fringe.threshold_with_children) == (
        Decimal(1000),
        Decimal(2000),
    )


def test_premio_di_risultato() -> None:
    """1% within 5,000 EUR, for incomes of the year before up to 80,000."""
    pdr = _RULES.pdr

    assert (pdr.flat_tax_rate, pdr.max_amount, pdr.income_ceiling) == (
        Decimal("0.01"),
        Decimal(5000),
        Decimal(80000),
    )


def test_renewal_increments() -> None:
    """5% on the 2026 increments, employment income of 2025 up to 33,000."""
    rinnovo = _RULES.rinnovo

    assert rinnovo is not None
    assert (rinnovo.flat_tax_rate, rinnovo.income_ceiling) == (
        Decimal("0.05"),
        Decimal(33000),
    )
    assert (rinnovo.valid_from_year, rinnovo.valid_until_year) == (2026, 2026)
    assert rinnovo.income_reference_year == 2025


def test_night_holiday_and_shift_pay() -> None:
    """15% within 1,500 EUR a year, employment income of 2025 up to 40,000."""
    regime = _RULES.notte_festivi_turni

    assert regime is not None
    assert (regime.flat_tax_rate, regime.annual_cap, regime.income_ceiling) == (
        Decimal("0.15"),
        Decimal(1500),
        Decimal(40000),
    )
    assert (regime.valid_from_year, regime.valid_until_year) == (2026, 2026)


def test_travel_allowance_caps_are_the_lire_of_the_text() -> None:
    """90,000 and 150,000 lire a day, less a third or two thirds."""
    travel = _RULES.travel_allowance

    assert (travel.italy.none, travel.italy.one, travel.italy.both) == (
        _euro(90000),
        _euro(60000),
        _euro(30000),
    )
    assert (travel.abroad.none, travel.abroad.one, travel.abroad.both) == (
        _euro(150000),
        _euro(100000),
        _euro(50000),
    )
