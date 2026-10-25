"""Hourly rate and supplements of the 8 pilot CCNLs, without caller rates.

Each run of March 2026 carries 4 overtime hours, 6 ordinary night hours and
8 holiday hours and states no hourly rate and no supplement amount where
the CCNL sets them.  The oracle is computed here from the table values the
bundle cites (base salary of the level in force on 1 March 2026, the fixed
allowances of the level, no seniority stated), the CCNL hourly divisor and
the CCNL percentages, in Decimal arithmetic rounded half up to the cent:

- overtime: ``hours * monthly * (1 + rate) / divisor``;
- supplement: ``hours * monthly * rate / divisor``.

Where the CCNL rate depends on facts the request does not carry (the night
window fixed by the company, the shift column of the metalmeccanici) or
the text is unconfirmed (Studi night work), the night amount stays the
caller's: the run reports it as caller-supplied, and omitting it rejects
the run.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import (
    AbsenceEvent,
    HolidayWorkEvent,
    HolidayWorkKind,
    NightShiftEvent,
    OvertimeEvent,
    ShiftKind,
    ShiftWorkEvent,
)
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_CENT = Decimal("0.01")
_OVERTIME_HOURS = Decimal(4)
_NIGHT_HOURS = Decimal(6)
_HOLIDAY_HOURS = Decimal(8)
_CALLER_NIGHT = Decimal("30.00")


@dataclass(frozen=True)
class Pilot:
    """A pilot CCNL with the table values its oracle is computed from.

    Attributes:
        slug: CCNL file stem.
        level: Level of the worker.
        monthly: Monthly pay elements of the CCNL hourly base, as printed
            in the cited tables.
        divisor: CCNL hourly divisor.
        overtime: Weekday overtime percentage.
        night: Ordinary night percentage; ``None`` when not derived.
        holiday: Holiday percentage.
        holiday_final: Whether the CCNL pays the holiday hours within the
            monthly pay (a final supplement) rather than apart or unsettled.
    """

    slug: str
    level: str
    monthly: tuple[str, ...]
    divisor: str
    overtime: str
    night: str | None
    holiday: str
    holiday_final: bool = False


_PILOTS = (
    # Art. 9 punti 2-3, art. 15 punto 1 (minimo + IPO D1 from 1 December
    # 2025), art. 20 punto 4 (175).
    Pilot(
        "chimica-farmaceutica-federchimica",
        "D1",
        ("2360.26",),
        "175",
        "0.10",
        None,
        "0.50",
    ),
    # Art. 148, 151 (172), 216 c.1 (25%), 219 (30%), 220 (20%); level 4.
    Pilot("turismo-federalberghi", "4", ("1660.69",), "172", "0.30", "0.25", "0.20"),
    # Art. 124 (25%), 126 (30%), 132 (20%), 157, 160 (172); level 4.
    Pilot(
        "pubblici-esercizi-fipe-angem", "4", ("1652.69",), "172", "0.30", "0.25", "0.20"
    ),
    # Art. 149 (15%, festivo 30%), 151 (15%), 206, 211 (168); level IV
    # paga base + contingenza 1781.68 and terzo elemento 2.07.
    Pilot(
        "terziario-confesercenti",
        "IV",
        ("1781.68", "2.07"),
        "168",
        "0.15",
        "0.15",
        "0.30",
    ),
    # Art. 29 (20%, festivo 55%), art. 38 (173); level 5.
    Pilot("metalmeccanico-confapi", "5", ("2195.87",), "173", "0.20", None, "0.55"),
    # Art. 7 (25%, festivo 50%), art. 3 Tit. IV (173); level C3.
    Pilot(
        "metalmeccanico-federmeccanica", "C3", ("2158.26",), "173", "0.25", None, "0.50"
    ),
    # Art. 95 (15%, festivo 30%), 97 E, 135, 137 (170); level 3S, no ENAC
    # (a role the worker does not hold).
    Pilot(
        "studi-professionali-confprofessioni",
        "3S",
        ("1722.01",),
        "170",
        "0.15",
        None,
        "0.30",
    ),
    # Art. 149, 151, 155, 206, 211 (168); level 4 paga base 1257.46,
    # contingenza + EDR 524.22, terzo elemento 2.07.
    Pilot(
        "commercio-confcommercio",
        "4",
        ("1257.46", "524.22", "2.07"),
        "168",
        "0.15",
        "0.15",
        "0.30",
    ),
)


def _cents(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _monthly(pilot: Pilot) -> Decimal:
    return sum((Decimal(v) for v in pilot.monthly), Decimal(0))


def _supplement(pilot: Pilot, hours: Decimal, rate: str) -> Decimal:
    return _cents(hours * _monthly(pilot) * Decimal(rate) / Decimal(pilot.divisor))


def _request(pilot: Pilot, *events: object) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50), provincial_pay_element=False),
        period_id=PeriodId(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_id=pilot.slug,
        level_code=pilot.level,
        opening_state=PeriodState.zero(),
        roles=frozenset(),
        events=events,  # type: ignore[arg-type]
    )


def _night(pilot: Pilot) -> NightShiftEvent:
    amount = _CALLER_NIGHT if pilot.night is None else None
    return NightShiftEvent(date(2026, 3, 11), amount, _NIGHT_HOURS)


def _run(pilot: Pilot) -> PeriodResult:
    result = calculate_period(
        _request(
            pilot,
            OvertimeEvent(date(2026, 3, 10), _OVERTIME_HOURS),
            _night(pilot),
            HolidayWorkEvent(date(2026, 3, 19), hours=_HOLIDAY_HOURS),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


def _decision(
    result: PeriodResult, capability: str, reason: str
) -> CalculationDecision:
    (found,) = [
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code == reason
    ]
    return found


@pytest.mark.parametrize("pilot", _PILOTS, ids=[p.slug for p in _PILOTS])
def test_overtime_is_paid_at_the_ccnl_hourly_base(pilot: Pilot) -> None:
    """4 h x (1 + rate) x monthly elements / divisor."""
    expected = _cents(
        _OVERTIME_HOURS
        * _monthly(pilot)
        * (1 + Decimal(pilot.overtime))
        / Decimal(pilot.divisor)
    )

    decision = _decision(_run(pilot), "overtime", "ccnl_hourly_rate_derived")

    assert decision.amount == expected
    assert decision.inputs["individual_elements"] == "none"
    assert decision.source is not None


@pytest.mark.parametrize("pilot", _PILOTS, ids=[p.slug for p in _PILOTS])
def test_holiday_hours_take_the_ccnl_supplement(pilot: Pilot) -> None:
    """8 h x rate x monthly / divisor, provisional where the hours are apart."""
    decision = _decision(_run(pilot), "holiday_work", "ccnl_supplement_applied")

    assert decision.amount == _supplement(pilot, _HOLIDAY_HOURS, pilot.holiday)
    assert decision.status is CalculationStatus.PROVISIONAL


@pytest.mark.parametrize(
    "pilot", [p for p in _PILOTS if p.night is not None], ids=lambda p: p.slug
)
def test_night_hours_take_the_ccnl_supplement(pilot: Pilot) -> None:
    """6 h x rate x monthly / divisor, inside the monthly pay: final."""
    assert pilot.night is not None
    decision = _decision(_run(pilot), "night_work", "ccnl_supplement_applied")

    assert decision.amount == _supplement(pilot, _NIGHT_HOURS, pilot.night)
    assert decision.status is CalculationStatus.FINAL


@pytest.mark.parametrize(
    "pilot", [p for p in _PILOTS if p.night is None], ids=lambda p: p.slug
)
def test_underived_night_work_stays_the_callers(pilot: Pilot) -> None:
    """The caller's night amount is applied and reported; omitted, rejected."""
    result = _run(pilot)
    (decision,) = [
        d
        for d in result.decisions
        if d.capability == "night_work" and d.origin is DecisionOrigin.CALLER_SUPPLIED
    ]
    assert decision.amount == _CALLER_NIGHT

    event = NightShiftEvent(date(2026, 3, 11), hours=_NIGHT_HOURS)
    with pytest.raises(InvalidInputError, match="no night supplement band"):
        calculate_period(
            _request(pilot, event),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )


def _pilot(slug: str) -> Pilot:
    return next(p for p in _PILOTS if p.slug == slug)


@pytest.mark.parametrize(
    "slug",
    [
        "turismo-federalberghi",
        "pubblici-esercizi-fipe-angem",
        "terziario-confesercenti",
        "studi-professionali-confprofessioni",
        "commercio-confcommercio",
    ],
)
def test_absence_days_are_deducted_at_a_26th(slug: str) -> None:
    """Two working days at monthly / 26 (verified by_26 absence rules)."""
    pilot = _pilot(slug)
    event = AbsenceEvent(
        date(2026, 3, 16), Decimal(16), end_date=date(2026, 3, 17), working_days=2
    )
    result = calculate_period(
        _request(pilot, event), repo=bundled_repository(), resolver=bundled_policies()
    )
    assert isinstance(result, PeriodResult)

    decision = _decision(result, "absence", "ccnl_absence_quota_applied")

    assert decision.amount == -_cents(2 * _monthly(pilot) / 26)


@pytest.mark.parametrize(
    "slug",
    [
        "chimica-farmaceutica-federchimica",
        "metalmeccanico-confapi",
        "metalmeccanico-federmeccanica",
    ],
)
def test_absence_on_a_derived_rule_stays_the_callers(slug: str) -> None:
    """An absence rule not verified leaves the rate to the caller."""
    event = AbsenceEvent(date(2026, 3, 16), Decimal(8), working_days=1)
    with pytest.raises(InvalidInputError, match="absence rule is not verified"):
        calculate_period(
            _request(_pilot(slug), event),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )


def test_turismo_night_qualified_staff_take_twelve_percent() -> None:
    """Art. 216 c.2: 12% for the role qualifica_notturna."""
    pilot = _pilot("turismo-federalberghi")
    request = _request(pilot, NightShiftEvent(date(2026, 3, 11), hours=_NIGHT_HOURS))
    roles = replace(request, roles=frozenset({"qualifica_notturna"}))

    result = calculate_period(
        roles, repo=bundled_repository(), resolver=bundled_policies()
    )
    assert isinstance(result, PeriodResult)

    decision = _decision(result, "night_work", "ccnl_supplement_applied")
    assert decision.amount == _supplement(pilot, _NIGHT_HOURS, "0.12")


def test_fipe_sunday_allowance_is_on_paga_base_and_contingenza() -> None:
    """Art. 130: 10% of base_salary / 172, seniority left out."""
    pilot = _pilot("pubblici-esercizi-fipe-angem")
    event = HolidayWorkEvent(
        date(2026, 3, 15), hours=_HOLIDAY_HOURS, kind=HolidayWorkKind.SUNDAY
    )
    result = calculate_period(
        _request(pilot, event), repo=bundled_repository(), resolver=bundled_policies()
    )
    assert isinstance(result, PeriodResult)

    decision = _decision(result, "holiday_work", "ccnl_supplement_applied")
    assert decision.amount == _supplement(pilot, _HOLIDAY_HOURS, "0.10")
    assert decision.inputs["hourly_base_method"] == "minimo_tabellare"
    assert decision.status is CalculationStatus.FINAL


def test_chimica_day_shift_takes_four_percent() -> None:
    """Art. 9 punto 5 a): 4% of the hourly base on the shift hours."""
    pilot = _pilot("chimica-farmaceutica-federchimica")
    event = ShiftWorkEvent(date(2026, 3, 12), hours=Decimal(8), kind=ShiftKind.DAY)
    result = calculate_period(
        _request(pilot, event), repo=bundled_repository(), resolver=bundled_policies()
    )
    assert isinstance(result, PeriodResult)

    decision = _decision(result, "shift_work", "ccnl_supplement_applied")
    assert decision.amount == _supplement(pilot, Decimal(8), "0.04")
