"""The statutory work-injury measures: their bands and the rate of a day."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.models import InjuryBand, InjuryRates


def test_the_rate_of_a_day_is_the_band_it_falls_in() -> None:
    """D.P.R. 1124/1965 art. 68: 60% to the ninetieth day, 75% after it."""
    injury = load_insured_absence_rates().injury

    assert [injury.rate_on(day) for day in (4, 90, 91, 200)] == [
        Decimal("0.60"),
        Decimal("0.60"),
        Decimal("0.75"),
        Decimal("0.75"),
    ]


@pytest.mark.parametrize("first_band", [3, 5])
def test_bands_start_the_day_after_the_waiting_period(first_band: int) -> None:
    """A band starting on or after a waiting day other than the next fails."""
    injury = load_insured_absence_rates().injury
    data = injury.model_dump()
    data["bands"] = [InjuryBand(day_from=first_band, rate=Decimal("0.60"))]

    with pytest.raises(ValidationError, match="day after the waiting period"):
        InjuryRates.model_validate(data)


def test_bands_are_in_day_order() -> None:
    """Two bands of the same first day are rejected."""
    injury = load_insured_absence_rates().injury
    band = InjuryBand(day_from=4, rate=Decimal("0.60"))
    data = injury.model_dump()
    data["bands"] = [band, band]

    with pytest.raises(ValidationError, match="day order"):
        InjuryRates.model_validate(data)
