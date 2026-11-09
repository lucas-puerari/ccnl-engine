"""A supplement band paid as a fixed amount per hour, without an hourly base."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.event.facade import NightShiftEvent
from ccnl_engine.working_time.hourly.policies import HourlyTerms
from ccnl_engine.working_time.supplement.policies import (
    SupplementPay,
    resolve_supplement,
    supplement_decision,
    supplement_issue,
)

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.working_time.models import TimeSupplements
    from ccnl_engine.working_time.supplement.models import SupplementBand

_SANITA = load_ccnl("sanita-privata-aiop-aris")
_COMMERCIO = load_ccnl("commercio-confcommercio")
_DAY = date(2026, 3, 16)
_CHAIN = MonthlyPayChain(base=Decimal("1680.00"), seniority=Decimal(0), allowances=())
_EVENT = NightShiftEvent(_DAY, hours=Decimal(8))


def _terms(ccnl: CCNL) -> HourlyTerms:
    return HourlyTerms(ccnl=ccnl, chain=_CHAIN, roles=frozenset())


def _supplements(ccnl: CCNL) -> TimeSupplements:
    rules = ccnl.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    return rules.time_supplements


def _night_band(ccnl: CCNL, code: str) -> SupplementBand:
    return next(b for b in _supplements(ccnl).supplement_bands if b.code == code)


def _fixed() -> SupplementPay:
    return resolve_supplement(_EVENT, _terms(_SANITA))


def test_a_fixed_band_pays_its_rate_per_hour() -> None:
    """Sanità art. 61(b): EUR 2.74 for each hour between 22:00 and 06:00."""
    pay = _fixed()

    assert pay.band.code == "NIGHT_FIXED"
    assert pay.base is None
    assert pay.amount == Decimal("21.92")  # 8 x 2.74


def test_a_percentage_band_keeps_its_hourly_base() -> None:
    """Commercio art. 153: the night band is a share of the hourly base."""
    pay = resolve_supplement(_EVENT, _terms(_COMMERCIO))

    assert pay.base is not None
    assert pay.amount == (pay.hours * pay.rate * pay.base.rate).quantize(
        Decimal("0.01")
    )


def test_the_decision_of_a_fixed_band_names_no_hourly_base() -> None:
    """The decision says the band is fixed and cites no base rule."""
    terms = _terms(_SANITA)
    inputs = supplement_decision(
        _EVENT, resolve_supplement(_EVENT, terms), terms
    ).inputs

    assert inputs["fixed_per_hour"] == "true"
    assert "hourly_base_rule" not in inputs
    assert "hourly_base_method" not in inputs
    assert inputs["band_code"] == "NIGHT_FIXED"


def test_the_decision_of_a_percentage_band_cites_its_base() -> None:
    """A band on the hourly base shows the base and its rule."""
    terms = _terms(_COMMERCIO)
    inputs = supplement_decision(
        _EVENT, resolve_supplement(_EVENT, terms), terms
    ).inputs

    assert inputs["fixed_per_hour"] == "false"
    assert inputs["hourly_base_rule"]
    assert "hourly_base_method" in inputs


@pytest.mark.parametrize(
    ("ccnl", "code", "words"),
    [
        (_SANITA, "NIGHT_FIXED", "worked on 2026-03-16 on top of"),
        (_COMMERCIO, "TDS_NOTTURNO", "worked on 2026-03-16 (hourly base "),
    ],
    ids=["fixed", "on-the-base"],
)
def test_the_issue_states_the_base_only_when_there_is_one(
    ccnl: CCNL, code: str, words: str
) -> None:
    """The issue of hours paid apart cites the hourly base of the band, if any."""
    band = _night_band(ccnl, code).model_copy(update={"hours_paid_apart": True})
    supplements = _supplements(ccnl).model_copy(update={"supplement_bands": (band,)})
    rules = ccnl.work_rules
    assert rules is not None
    work = rules.model_copy(update={"time_supplements": supplements})
    changed = ccnl.model_copy(update={"work_rules": work})

    issue = supplement_issue(_EVENT, resolve_supplement(_EVENT, _terms(changed)))

    assert issue is not None
    assert words in issue.message
