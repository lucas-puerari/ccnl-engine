"""G01 overtime: the 48th weekly hour, ANCC art. 126 and Fiori art. 33.

``OvertimeEvent.weekly_hours_before`` counts every hour worked in the week:
the band 'eccedente la 48a ora' starts at 48.  Commercio art. 149, two hours
after 47: one at 15%, one at 20% (multiplier 1.175).  ANCC art. 126: 20%
up to the 48th hour, 35% on holidays, 55% at night; art. 121 ordinary night
25%.  Fiori art. 33: 30%, 55% beyond the 48th hour, 55% holiday, 70% night,
75% night-holiday; art. 31 holiday work 50%.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import NoPensionFund, Permanent
from tests.knowledge.ccnl_engine.irpef.other_income.builders import employment_only
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period


def _multiplier(before: Decimal) -> Decimal:
    result = regular_period(
        employment=Employment(
            ccnl_id="commercio-confcommercio",
            level_code="4",
            seniority=new_hire(),
            pension_fund=NoPensionFund(),
            contract_type=Permanent(),
        ),
        current_year=employment_only(),
        events=(
            OvertimeEvent(date(2026, 1, 15), Decimal(2), weekly_hours_before=before),
        ),
    )
    (decision,) = [
        d for d in result.decisions if d.reason_code == "ccnl_overtime_band_applied"
    ]
    multiplier = decision.inputs["multiplier"]
    assert isinstance(multiplier, Decimal)
    return multiplier


@pytest.mark.parametrize(
    ("before", "multiplier"),
    [
        (Decimal(40), Decimal("1.15")),
        (Decimal(47), Decimal("1.175")),
        (Decimal(48), Decimal("1.20")),
    ],
)
def test_the_twenty_percent_starts_after_the_48th_hour(
    before: Decimal, multiplier: Decimal
) -> None:
    """Hours 41-48 at 15%, beyond at 20%."""
    assert _multiplier(before) == multiplier


def _rates(slug: str) -> dict[str, tuple[str, Decimal | None]]:
    work = load_ccnl(slug).work_rules
    assert work is not None
    assert work.time_supplements is not None
    supplements = work.time_supplements
    bands = {
        b.code: (str(b.rate.value_at(date(2026, 6, 1))), b.hour_threshold_per_week)
        for b in supplements.overtime_bands
    }
    bands.update({
        b.code: (str(b.rate.value_at(date(2026, 6, 1))), None)
        for b in supplements.supplement_bands
    })
    return bands


def test_ancc_rates_of_articles_121_to_132() -> None:
    """20/25/35/55% overtime, ordinary night 25%, rest day and holiday 35%."""
    assert _rates("distribuzione-cooperativa-ancc") == {
        "OT_DIURNO": ("0.20", None),
        "OT_DIURNO_EXTRA": ("0.25", 48),
        "OT_FESTIVO": ("0.35", None),
        "OT_NOTTURNO": ("0.55", None),
        "OT_NOTTURNO_FESTIVO": ("0.55", None),
        "ANCC_NOTTURNO": ("0.25", None),
        "ANCC_FESTIVO": ("0.35", None),
        "ANCC_RIPOSO": ("0.35", None),
    }


def test_fiori_rates_of_articles_31_and_33() -> None:
    """30/55/55/70/75% overtime, holiday work 50%."""
    assert _rates("fiori-recisi-ancef") == {
        "OT_DIURNO": ("0.30", None),
        "OT_DIURNO_EXTRA": ("0.55", 48),
        "OT_FESTIVO": ("0.55", None),
        "OT_NOTTURNO": ("0.70", None),
        "OT_NOTTURNO_FESTIVO": ("0.75", None),
        "FIORI_FESTIVO": ("0.50", None),
    }
