"""Hourly base of a CCNL: when it is derived and what it is made of."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.working_time.hourly.policies import HourlyTerms
from ccnl_engine.working_time.models import HourlyBaseMethod

_COMMERCIO = load_ccnl("commercio-confcommercio")
_DAY = date(2026, 3, 10)
_CHAIN = MonthlyPayChain(
    base=Decimal("1500.00"), seniority=Decimal("50.00"), allowances=()
)


def _terms(**changes: object) -> HourlyTerms:
    values: dict[str, object] = {
        "ccnl": _COMMERCIO,
        "chain": _CHAIN,
        "ruleset": "ccnl/commercio-confcommercio",
    }
    values.update(changes)
    return HourlyTerms(**values)  # type: ignore[arg-type]


def _reject(terms: HourlyTerms, day: date = _DAY) -> str:
    with pytest.raises(InvalidInputError) as caught:
        terms.base(day, "OvertimeEvent.hourly_rate", "overtime")
    return str(caught.value)


def test_default_terms_derive_nothing() -> None:
    """Without a CCNL there is no verified hourly base."""
    assert "has no verified hourly base" in _reject(HourlyTerms())


def test_unsourced_hourly_base_is_not_read() -> None:
    """A CCNL whose hourly base carries no provenance is not derived."""
    ccnl = load_ccnl("alimentari-federalimentare")

    assert "has no verified hourly base" in _reject(_terms(ccnl=ccnl))


def test_another_full_time_week_is_not_derived() -> None:
    """Commercio divides by 168 for 40 hours: a 45-hour week is rejected."""
    message = _reject(_terms(full_time_weekly_hours=Decimal(45)))

    assert "40-hour week" in message
    assert "full-time week of 45 hours" in message


def test_a_day_without_divisor_is_not_derived() -> None:
    """Before the first divisor period no rate is derived."""
    assert "has no hourly divisor" in _reject(_terms(), date(2020, 1, 1))


def test_the_band_method_overrides_the_ccnl_one() -> None:
    """A band with its own base divides the base salary only."""
    base = _terms().base(_DAY, "f", "overtime", HourlyBaseMethod.MINIMO_TABELLARE)

    assert base.components == (("base_salary", Decimal("1500.00")),)
    assert base.rate == Decimal("1500.00") / Decimal(168)


def test_minimo_e_anzianita_leaves_the_allowances_out() -> None:
    """Chimica: base salary and seniority, no allowance."""
    chimica = load_ccnl("chimica-farmaceutica-federchimica")
    allowance = next(a for lv in chimica.levels for a in lv.fixed_allowances)
    chain = MonthlyPayChain(
        base=Decimal("2000.00"),
        seniority=Decimal("40.00"),
        allowances=((allowance, Decimal("30.00")),),
    )

    base = _terms(ccnl=chimica, chain=chain).base(_DAY, "f", "overtime")

    assert base.monthly == Decimal("2040.00")
    assert base.inputs()["hourly_base[seniority]"] == Decimal("40.00")
