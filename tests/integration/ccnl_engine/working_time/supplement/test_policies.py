"""Choice of the CCNL supplement band of a night, holiday or shift event."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import (
    HolidayWorkEvent,
    HolidayWorkKind,
    NightShiftEvent,
    ShiftKind,
    ShiftWorkEvent,
)
from ccnl_engine.working_time.hourly.policies import HourlyTerms
from ccnl_engine.working_time.supplement.models import SupplementBand, SupplementWork
from ccnl_engine.working_time.supplement.policies import (
    HOURS_NOT_POSTED,
    resolve_supplement,
    supplement_issue,
    work_of,
)

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

_COMMERCIO = load_ccnl("commercio-confcommercio")
_DAY = date(2026, 3, 15)
_CHAIN = MonthlyPayChain(base=Decimal("1680.00"), seniority=Decimal(0), allowances=())
_HOURS = Decimal(8)


def _with_bands(bands: tuple[SupplementBand, ...]) -> CCNL:
    rules = _COMMERCIO.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    supplements = rules.time_supplements.model_copy(update={"supplement_bands": bands})
    work = rules.model_copy(update={"time_supplements": supplements})
    return _COMMERCIO.model_copy(update={"work_rules": work})


def _bands() -> tuple[SupplementBand, ...]:
    rules = _COMMERCIO.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    return rules.time_supplements.supplement_bands


def _terms(ccnl: CCNL = _COMMERCIO, **changes: object) -> HourlyTerms:
    values: dict[str, object] = {"ccnl": ccnl, "chain": _CHAIN, "roles": frozenset()}
    values.update(changes)
    return HourlyTerms(**values)  # type: ignore[arg-type]


def _sunday() -> HolidayWorkEvent:
    return HolidayWorkEvent(_DAY, hours=_HOURS, kind=HolidayWorkKind.SUNDAY)


def test_the_role_band_applies_to_its_role() -> None:
    """Art. 157: 10% at the motorway fuel stations."""
    terms = _terms(roles=frozenset({"impianto_carburante_autostradale"}))

    pay = resolve_supplement(_sunday(), terms)

    assert pay.band.code == "TDS_DOMENICA_AUTOSTRADE"
    assert pay.amount == Decimal("8.00")  # 8 x 0.10 x 1680 / 168


def test_without_the_role_the_plain_band_applies() -> None:
    """Art. 153: 30% for a worker holding none of the roles."""
    assert resolve_supplement(_sunday(), _terms()).amount == Decimal("24.00")


def test_unknown_roles_leave_the_band_open() -> None:
    """A role band and unstated roles: the caller states the amount."""
    with pytest.raises(InvalidInputError, match=r"Employment\.roles is not stated"):
        resolve_supplement(_sunday(), _terms(roles=None))


def test_a_band_of_roles_only_needs_one_of_them() -> None:
    """Without a plain band, a worker holding no role has none."""
    only_role = tuple(b for b in _bands() if b.code != "TDS_DOMENICA")

    with pytest.raises(InvalidInputError, match="only for the roles"):
        resolve_supplement(_sunday(), _terms(_with_bands(only_role)))


def test_a_band_of_another_level_does_not_apply() -> None:
    """A band reserved to other levels leaves the work without a band."""
    night = next(b for b in _bands() if b.code == "TDS_NOTTURNO")
    other = night.model_copy(update={"levels": ("Q",)})
    terms = _terms(_with_bands((other,)), level_code="4")

    with pytest.raises(InvalidInputError, match="no night supplement band"):
        resolve_supplement(NightShiftEvent(_DAY, hours=_HOURS), terms)


def test_a_shift_needs_its_kind() -> None:
    """A shift event of no kind has no band to choose."""
    with pytest.raises(InvalidInputError, match=r"ShiftWorkEvent\.kind is not stated"):
        resolve_supplement(ShiftWorkEvent(_DAY, hours=_HOURS), _terms())


def test_work_of_each_event() -> None:
    """Night, the holiday kind, the shift kind."""
    assert work_of(NightShiftEvent(_DAY, hours=_HOURS)) is SupplementWork.NIGHT
    assert work_of(_sunday()) is SupplementWork.SUNDAY
    shift = ShiftWorkEvent(_DAY, hours=_HOURS, kind=ShiftKind.NIGHT)
    assert work_of(shift) is SupplementWork.NIGHT_SHIFT


@pytest.mark.parametrize(
    ("paid_apart", "words"),
    [(True, "pays the 8 hours"), (None, "does not settle whether")],
)
def test_hours_paid_apart_raise_an_issue(paid_apart: bool | None, words: str) -> None:
    """The hours themselves are not posted: the issue says so."""
    holiday = next(b for b in _bands() if b.code == "TDS_FESTIVO")
    band = holiday.model_copy(update={"hours_paid_apart": paid_apart})
    event = HolidayWorkEvent(_DAY, hours=_HOURS)
    pay = resolve_supplement(event, _terms(_with_bands((band,))))

    issue = supplement_issue(event, pay)

    assert issue is not None
    assert issue.code == HOURS_NOT_POSTED
    assert words in issue.message
