"""The cut of the agricultural employer contributions by zone.

INPS circ. 43/2026 par. 7: 75% in the zone particolarmente svantaggiate
(ex montane), 68% in the svantaggiate, never on the 0.30% of art. 25 c. 4
L. 845/1978.  Each employer rate r becomes r - share x (r - 0.30%).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.tax.contribution.models import InpsRates
from ccnl_engine.tax.contribution.models_zone_reduction import (
    AgriculturalZone,
    ZoneReduction,
    with_zone_reduction,
)

_CUT = ZoneReduction(
    disadvantaged=Decimal("0.68"),
    mountain=Decimal("0.75"),
    excluded_rate=Decimal("0.0030"),
)
_RATES = InpsRates(
    employee_rate=Decimal("0.0884"),
    employee_ivs_rate=Decimal("0.0884"),
    employer_rate=Decimal("0.25453"),
    employer_ivs_rate=Decimal("0.2166"),
    ceiling=Decimal("122295.00"),
    employer_rate_by_category={WorkerCategory.IMPIEGATO: Decimal("0.2563")},
    employer_fixed_term_rate_by_category={WorkerCategory.OPERAIO: Decimal("0.25253")},
    zone_reduction=_CUT,
)


@pytest.mark.parametrize(
    ("zone", "share"),
    [
        (AgriculturalZone.ORDINARY, Decimal(0)),
        (AgriculturalZone.DISADVANTAGED, Decimal("0.68")),
        (AgriculturalZone.MOUNTAIN, Decimal("0.75")),
    ],
)
def test_share_of_each_zone(zone: AgriculturalZone, share: Decimal) -> None:
    """No cut in an ordinary zone, 68% and 75% in the others."""
    assert _CUT.share(zone) == share


def test_disadvantaged_zone_cuts_every_employer_rate_but_the_0_30() -> None:
    """25.453% becomes 25.453 - 0.68 x 25.153 = 8.34896%; IVS 21.66 x 0.32."""
    rates = with_zone_reduction(_RATES, AgriculturalZone.DISADVANTAGED)
    assert rates.employer_rate == Decimal("0.0834896")
    assert rates.employer_ivs_rate == Decimal("0.069312")
    assert rates.employer_rate_by_category[WorkerCategory.IMPIEGATO] == Decimal(
        "0.084056"
    )
    assert rates.employer_fixed_term_rate_by_category[
        WorkerCategory.OPERAIO
    ] == Decimal("0.0828496")
    assert rates.employee_rate == _RATES.employee_rate


def test_ordinary_zone_keeps_the_rates() -> None:
    """No cut, no open fact."""
    assert with_zone_reduction(_RATES, AgriculturalZone.ORDINARY) == _RATES


def test_unknown_zone_flags_the_rates() -> None:
    """The full rates, flagged for a missing_fact issue."""
    rates = with_zone_reduction(_RATES, None)
    assert rates.zone_reduction_open
    assert rates.employer_rate == _RATES.employer_rate


def test_sector_without_the_cut_is_unchanged() -> None:
    """Outside agricoltura the zone is not read."""
    rates = _RATES.model_copy(update={"zone_reduction": None})
    assert with_zone_reduction(rates, None) == rates
