"""Minimum of the art. 13 c. 1 lett. a) TUIR deduction in the withholding.

Art. 13 c. 1 lett. a) TUIR, Normattiva, text in force on 7 October 2026
(https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art13):
"L'ammontare della detrazione effettivamente spettante non può essere
inferiore a 690 euro. Per i rapporti di lavoro a tempo determinato,
l'ammontare della detrazione effettivamente spettante non può essere
inferiore a 1.380 euro".

Istruzioni per la compilazione della Certificazione Unica 2026, Agenzia delle
Entrate, updated 24 February 2026, punto 367, p. 33
(https://www.agenziaentrate.gov.it/portale/documents/20143/9602395/CU_istr_2026_agg+24+02.pdf/4184818b-05a3-acce-5956-70811c7d2233,
sha256 a6ccf7cf53edcbd0d084c2266868649f8d17c348644401b540efd5e3fc95e841): for
an employment "di durata inferiore all'anno" "il sostituto deve ragguagliare
anche la detrazione minima al periodo di lavoro", and the worker "potrà
fruire della detrazione per l'intero anno in sede di dichiarazione dei
redditi".  The tax return grants the minimum whole (Allegato C to the
730/2026 instructions, par. 19.9.1, p. 339) and the deduction is due only
when the days of work (rigo C5) are filled.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.service.irpef_deductions import (
    minimum_left_to_tax_return,
    work_income_deduction,
)
from ccnl_engine.tax.domain.irpef_rules import (
    WorkDeductionMinimum,
    WorkDeductionRules,
)

_FLAT_BAND = Decimal(10_000)


@pytest.mark.parametrize(
    ("days", "fixed_term", "expected"),
    [
        # 1,955 * 92 / 365 = 492.767..., 492.77; the floor for the days is
        # 690 * 92 / 365 = 173.92 or 1,380 * 92 / 365 = 347.84.
        pytest.param(92, False, Decimal("492.77"), id="open-ended-92"),
        pytest.param(92, True, Decimal("492.77"), id="fixed-term-92"),
        # 1,955 * 200 / 365 = 1,071.232..., 1,071.23; the floor 378.08 or
        # 756.16.
        pytest.param(200, False, Decimal("1071.23"), id="open-ended-200"),
        pytest.param(200, True, Decimal("1071.23"), id="fixed-term-200"),
        # Full year: 1,955 against 690 or 1,380.
        pytest.param(365, False, Decimal("1955.00"), id="open-ended-full-year"),
        pytest.param(365, True, Decimal("1955.00"), id="fixed-term-full-year"),
    ],
)
def test_flat_band_proportions_the_floor_to_the_days(
    days: int, *, fixed_term: bool, expected: Decimal
) -> None:
    """Up to 15,000 EUR the larger of 1,955 and the floor, both for the days.

    With the 2026 amounts the floor for the days never exceeds 1,955 for the
    days, so the withholding deducts 1,955 x days / 365.
    """
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
    assert minimum_left_to_tax_return(income, days, fixed_term=True) == Decimal(0)


def test_floor_comes_from_the_rules() -> None:
    """A versioned minimum above 1,955 wins, proportioned to the days.

    Minimum 2,000 for 92 days: 2,000 * 92 / 365 = 504.109..., 504.11, above
    492.77; 2,400 for a fixed term: 2,400 * 92 / 365 = 604.931..., 604.93.
    """
    rules = WorkDeductionRules(
        minimum=WorkDeductionMinimum(open_ended=Decimal(2000), fixed_term=Decimal(2400))
    )
    open_ended = work_income_deduction(_FLAT_BAND, 92, rules)
    fixed_term = work_income_deduction(_FLAT_BAND, 92, rules, fixed_term=True)
    assert (open_ended, fixed_term) == (Decimal("504.11"), Decimal("604.93"))


@pytest.mark.parametrize(
    ("income", "days", "fixed_term", "expected"),
    [
        # 690 - 492.77 and 1,380 - 492.77.
        pytest.param(_FLAT_BAND, 92, False, Decimal("197.23"), id="open-ended-92"),
        pytest.param(_FLAT_BAND, 92, True, Decimal("887.23"), id="fixed-term-92"),
        # 1,071.23 is above 690; 1,380 - 1,071.23 = 308.77.
        pytest.param(_FLAT_BAND, 200, False, Decimal(0), id="open-ended-200"),
        pytest.param(_FLAT_BAND, 200, True, Decimal("308.77"), id="fixed-term-200"),
        # 1,955 is above both floors.
        pytest.param(_FLAT_BAND, 365, True, Decimal(0), id="full-year"),
        # 15,000 is still in lett. a): 690 - 492.77.
        pytest.param(Decimal(15_000), 92, False, Decimal("197.23"), id="flat-band-top"),
        # Above 15,000 lett. a) and its minimum do not apply.
        pytest.param(Decimal(20_000), 30, True, Decimal(0), id="above-flat-band"),
    ],
)
def test_minimum_left_to_tax_return(
    income: Decimal, days: int, *, fixed_term: bool, expected: Decimal
) -> None:
    """The whole minimum less the deduction of the withholding, at least 0."""
    balance = minimum_left_to_tax_return(income, days, fixed_term=fixed_term)
    assert balance == expected
