"""The INPS daily base (RMGG) of INPS circ. 134368/1981, point 11.

Every expected value is computed by hand from the circular: an impiegato
divides the pay and the monthly share of the recurring payments by 30; an
operaio divides the pay by the days worked or paid and the share by 25.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.base.inputs import InpsSicknessBase
from ccnl_engine.sickness.base.rules import daily_base, episode_daily_base
from ccnl_engine.sickness.models import SicknessEpisode, SicknessHistory
from ccnl_engine.sickness.term.rules import SicknessTerms

_PAY = Decimal("1800.00")
_THIRTEEN = Decimal(13)


def test_an_impiegato_divides_by_thirty() -> None:
    """(1800 + 1800 / 12) / 30 = 1950 / 30 = 65."""
    base = InpsSicknessBase(_PAY, Decimal(0))

    assert daily_base(base, WorkerCategory.IMPIEGATO, _THIRTEEN) == Decimal(65)


def test_a_fourteenth_and_a_bonus_join_the_monthly_share() -> None:
    """Share (1800 * 2 + 1200) / 12 = 400; (1800 + 400) / 30 = 73.33..."""
    base = InpsSicknessBase(_PAY, Decimal(1200))

    rmgg = daily_base(base, WorkerCategory.QUADRO, Decimal(14))

    assert rmgg == (Decimal(2200) / 30)


def test_an_operaio_divides_the_pay_by_the_days_and_the_share_by_25() -> None:
    """1800 / 24 + 150 / 25 = 75 + 6 = 81."""
    base = InpsSicknessBase(_PAY, Decimal(0), paid_days=24)

    assert daily_base(base, WorkerCategory.OPERAIO, _THIRTEEN) == Decimal(81)


@pytest.mark.parametrize(
    ("base", "category"),
    [
        (InpsSicknessBase(_PAY, Decimal(0)), WorkerCategory.OPERAIO),
        (InpsSicknessBase(_PAY, Decimal(0), paid_days=24), None),
        (
            InpsSicknessBase(Decimal(900), Decimal(0), paid_days=15),
            WorkerCategory.IMPIEGATO,
        ),
    ],
    ids=["operaio_without_days", "unknown_category", "partial_month_without_whole"],
)
def test_an_untold_base_is_none(
    base: InpsSicknessBase, category: WorkerCategory | None
) -> None:
    """Without the days of an operaio, the category or a whole month, no base."""
    assert daily_base(base, category, _THIRTEEN) is None


def test_an_impiegato_of_a_partial_month_takes_the_share_of_a_whole_month() -> None:
    """Point 11.2 d-f: 900 / 15 + (1800 / 12) / 30 = 60 + 5 = 65."""
    base = InpsSicknessBase(Decimal(900), Decimal(0), paid_days=15, full_month_pay=_PAY)

    assert daily_base(base, WorkerCategory.IMPIEGATO, _THIRTEEN) == Decimal(65)


def test_an_operaio_hired_in_the_month_takes_the_share_of_a_whole_month() -> None:
    """900 / 12 + (1800 / 12) / 25 = 75 + 6 = 81."""
    base = InpsSicknessBase(Decimal(900), Decimal(0), paid_days=12, full_month_pay=_PAY)

    assert daily_base(base, WorkerCategory.OPERAIO, _THIRTEEN) == Decimal(81)


def test_twelve_payments_have_no_share() -> None:
    """A CCNL of twelve monthly payments adds nothing: 1800 / 30 = 60."""
    base = InpsSicknessBase(_PAY, Decimal(0))

    assert daily_base(base, WorkerCategory.IMPIEGATO, Decimal(12)) == Decimal(60)


@pytest.mark.parametrize(
    ("fields", "match"),
    [
        ({"theoretical_pay": Decimal(-1)}, "theoretical_pay"),
        ({"recurring_annual": Decimal(-1)}, "recurring_annual"),
        ({"paid_days": 0}, "paid_days"),
        ({"paid_days": 32}, "paid_days"),
        ({"full_month_pay": Decimal(-1)}, "full_month_pay"),
    ],
)
def test_a_malformed_base_is_rejected(fields: dict[str, object], match: str) -> None:
    """Amounts are non-negative, the days a count of one month."""
    values: dict[str, object] = {
        "theoretical_pay": _PAY,
        "recurring_annual": Decimal(0),
        **fields,
    }
    with pytest.raises(InvalidInputError, match=match):
        InpsSicknessBase(**values)  # type: ignore[arg-type]


def _series(valid_from: str) -> TimeSeries:
    return TimeSeries.model_validate({
        "periods": [{"valid_from": valid_from, "valid_until": None, "value": "13"}]
    })


_EPISODE = SicknessEpisode(
    "E",
    date(2026, 5, 25),
    date(2026, 5, 29),
    inps_base=InpsSicknessBase(_PAY, Decimal(0)),
)
_TERMS = SicknessTerms(
    category=WorkerCategory.IMPIEGATO, monthly_payments=_series("2026-01-01")
)


def test_the_episode_reads_the_payments_of_the_month_before() -> None:
    """The April payments: 13, so (1800 + 150) / 30 = 65."""
    assert episode_daily_base(_EPISODE, _TERMS) == Decimal(65)


def test_the_payments_are_those_of_the_last_day_of_the_month_before() -> None:
    """Payments in force from 30 April count for an episode of 25 May."""
    terms = replace(_TERMS, monthly_payments=_series("2026-04-30"))

    assert episode_daily_base(_EPISODE, terms) == Decimal(65)


@pytest.mark.parametrize(
    "terms",
    [
        replace(_TERMS, general_regime=False),
        replace(_TERMS, monthly_payments=None),
        replace(_TERMS, monthly_payments=_series("2026-05-01")),
    ],
    ids=["sector_regime", "no_payments", "payments_after_the_month_before"],
)
def test_no_base_without_the_general_regime_or_the_payments(
    terms: SicknessTerms,
) -> None:
    """A sector regime, or no payments on 30 April, leave the quota."""
    assert episode_daily_base(_EPISODE, terms) is None


def test_a_relapse_chain_without_a_base_has_none() -> None:
    """No episode of the chain states a base, even through a cycle."""
    first = SicknessEpisode("A", date(2026, 5, 4), date(2026, 5, 8), relapse_of="B")
    second = SicknessEpisode("B", date(2026, 5, 11), date(2026, 5, 12), relapse_of="A")
    terms = replace(_TERMS, history=SicknessHistory((first, second)))

    assert episode_daily_base(second, terms) is None
