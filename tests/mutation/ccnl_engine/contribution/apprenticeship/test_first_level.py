"""Contributions of a first-level apprentice: INPS circ. 108/2018 par. 3.4.

"l'aliquota contributiva del 10% [...] è ridotta alla misura del 5%", with
no NASpI and no 0.30%; a firm with up to nine employees keeps 1.5% in the
first year and 3% in the second; no dismissal contribution.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.contribution.apprenticeship.rules import first_level_employer_rate
from ccnl_engine.contribution.rate.models import ApprenticeRates
from ccnl_engine.employment.apprentice.inputs import ApprenticeshipProgramme
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.employment.period.causes import TerminationCause
from ccnl_engine.termination.naspi.rules import is_due

_LARGE = ApprenticeRates(
    employee_rate=Decimal("0.0584"),
    employee_ivs_rate=Decimal("0.0584"),
    employer_rate_months_0_11=Decimal("0.1161"),
    employer_ivs_rate_months_0_11=Decimal("0.10"),
    employer_rate_months_12_23=Decimal("0.1161"),
    employer_ivs_rate_months_12_23=Decimal("0.10"),
    employer_rate_after=Decimal("0.1161"),
    employer_ivs_rate_after=Decimal("0.10"),
)
_SMALL = _LARGE.model_copy(
    update={
        "employer_ivs_rate_months_0_11": Decimal("0.015"),
        "employer_ivs_rate_months_12_23": Decimal("0.03"),
    }
)


@pytest.mark.parametrize(
    ("rates", "months", "rate"),
    [
        (_LARGE, 0, "0.05"),
        (_LARGE, 30, "0.05"),
        (_SMALL, 0, "0.015"),
        (_SMALL, 12, "0.03"),
        (_SMALL, 24, "0.05"),
    ],
    ids=["large-first", "large-later", "small-first", "small-second", "small-third"],
)
def test_the_employer_rate(rates: ApprenticeRates, months: int, rate: str) -> None:
    """5%, or the lower rate of a small firm in the first two years."""
    assert first_level_employer_rate(rates, months) == Decimal(rate)


@pytest.mark.parametrize(
    ("programme", "owed"),
    [
        (ApprenticeshipProgramme.FIRST_LEVEL, False),
        (ApprenticeshipProgramme.THIRD_LEVEL, True),
        (ApprenticeshipProgramme.PROFESSIONALISING, True),
    ],
)
def test_the_dismissal_contribution(
    programme: ApprenticeshipProgramme,
    owed: bool,
) -> None:
    """Lett. a: no dismissal contribution for a first-level apprentice."""
    apprentice = Apprentice(months_elapsed=6, programme=programme)
    assert is_due(TerminationCause.DISMISSAL, None, apprentice) is owed
