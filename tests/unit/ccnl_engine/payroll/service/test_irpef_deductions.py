"""Minimum of the art. 13 c. 1 lett. a) TUIR deduction.

Art. 13 c. 1 lett. a) TUIR, Normattiva, text in force on 7 October 2026
(https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art13):
"L'ammontare della detrazione effettivamente spettante non può essere
inferiore a 690 euro. Per i rapporti di lavoro a tempo determinato,
l'ammontare della detrazione effettivamente spettante non può essere
inferiore a 1.380 euro".  Allegato C to the 730/2026 instructions, par.
19.9.1, p. 339: the minimum "non deve essere rapportata ai giorni di lavoro
dipendente" and the deduction due is the larger of the two amounts; the
deduction is due only when the days of work (rigo C5) are filled.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.service.irpef_deductions import work_income_deduction
from ccnl_engine.tax.domain.irpef_rules import (
    WorkDeductionMinimum,
    WorkDeductionRules,
)

_FLAT_BAND = Decimal(10_000)


@pytest.mark.parametrize(
    ("days", "fixed_term", "expected"),
    [
        # 1,955 * 92 / 365 = 492.7671...: below both floors.
        pytest.param(92, False, Decimal("690.00"), id="open-ended-92"),
        pytest.param(92, True, Decimal("1380.00"), id="fixed-term-92"),
        # 1,955 * 200 / 365 = 1,071.2328...: above 690, below 1,380.
        pytest.param(200, False, Decimal("1071.23"), id="open-ended-200"),
        pytest.param(200, True, Decimal("1380.00"), id="fixed-term-200"),
        # Full year: 1,955, above both floors.
        pytest.param(365, False, Decimal("1955.00"), id="open-ended-full-year"),
        pytest.param(365, True, Decimal("1955.00"), id="fixed-term-full-year"),
    ],
)
def test_flat_band_takes_the_larger_of_formula_and_floor(
    days: int, *, fixed_term: bool, expected: Decimal
) -> None:
    """Up to 15,000 EUR the deduction is at least the floor of the contract."""
    deduction = work_income_deduction(_FLAT_BAND, days, fixed_term=fixed_term)
    assert deduction == expected


def test_floor_is_not_applied_above_the_flat_band() -> None:
    """Income 20,000 EUR over 30 days: lett. b) has no minimum.

    1,910 + 1,190 * 0.6153 (8,000 / 13,000 truncated) = 2,642.21 for the
    year; * 30 / 365 = 217.1679..., 217.17.
    """
    deduction = work_income_deduction(Decimal(20_000), 30, fixed_term=True)
    assert deduction == Decimal("217.17")


@pytest.mark.parametrize(
    ("income", "days"),
    [
        pytest.param(Decimal(0), 92, id="no-income"),
        pytest.param(_FLAT_BAND, 0, id="no-days"),
    ],
)
def test_no_floor_without_income_or_days(income: Decimal, days: int) -> None:
    """Without employment income or days of work no deduction is due."""
    assert work_income_deduction(income, days, fixed_term=True) == Decimal(0)


def test_floor_comes_from_the_rules() -> None:
    """The versioned minimum of the rules replaces the 2026 default."""
    rules = WorkDeductionRules(
        minimum=WorkDeductionMinimum(open_ended=Decimal(700), fixed_term=Decimal(1400))
    )
    open_ended = work_income_deduction(_FLAT_BAND, 92, rules)
    fixed_term = work_income_deduction(_FLAT_BAND, 92, rules, fixed_term=True)
    assert (open_ended, fixed_term) == (Decimal("700.00"), Decimal("1400.00"))
