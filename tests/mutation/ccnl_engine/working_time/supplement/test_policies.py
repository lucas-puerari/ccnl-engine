"""Choice of the CCNL supplement band of a night, holiday or shift event."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.decision.models import CalculationStatus, IssueCause
from ccnl_engine.errors import InvalidInputError, MissingRuleError
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
    supplement_decision,
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
    with pytest.raises(InvalidInputError, match=r"Employment\.roles is not") as error:
        resolve_supplement(_sunday(), _terms(roles=None))

    assert error.value.field == "Employment.roles"


def test_a_band_of_roles_only_needs_one_of_them() -> None:
    """Without a plain band, a worker holding no role has none."""
    only_role = tuple(b for b in _bands() if b.code != "TDS_DOMENICA")

    with pytest.raises(MissingRuleError, match="only for the roles"):
        resolve_supplement(_sunday(), _terms(_with_bands(only_role)))


def test_a_band_of_another_level_does_not_apply() -> None:
    """A band reserved to other levels leaves the work without a band."""
    night = next(b for b in _bands() if b.code == "TDS_NOTTURNO")
    other = night.model_copy(update={"levels": ("Q",)})
    terms = _terms(_with_bands((other,)), level_code="4")

    with pytest.raises(MissingRuleError, match="no night supplement band"):
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


def test_sunday_decision_identifies_the_rule_and_each_factor() -> None:
    """Art. 153: eight hours at 30% of EUR 1680 / 168 = EUR 24."""
    event = _sunday()
    terms = _terms()
    pay = resolve_supplement(event, terms)
    decision = supplement_decision(event, pay, terms)

    assert pay.amount == Decimal("24.00")
    assert pay.hours == Decimal(8)
    assert pay.rate == Decimal("0.30")
    assert pay.base is not None
    assert pay.base.rate == Decimal(10)
    assert decision.amount == Decimal("24.00")
    assert decision.capability == "holiday_work"
    assert decision.reason_code == "ccnl_supplement_applied"
    assert decision.status is CalculationStatus.FINAL
    assert decision.rule == terms.rule_of(
        "work_rules.time_supplements.supplement_bands[TDS_DOMENICA]"
    )
    assert decision.inputs["work"] == "sunday"
    assert decision.inputs["band_code"] == "TDS_DOMENICA"
    assert decision.inputs["band_supplement"] == Decimal("0.30")
    assert decision.inputs["hours"] == Decimal(8)
    assert decision.inputs["hourly_base_rule"] == terms.rule_of(
        "work_rules.time_supplements.hourly_base_method"
    )
    assert decision.inputs["hours_paid_apart"] == "no"
    assert "in_periodic_shift" not in decision.inputs
    assert decision.source == pay.band.provenance.location
    assert decision.source is not None
    assert supplement_issue(event, pay) is None


@pytest.mark.parametrize(
    ("paid_apart", "status", "label", "message"),
    [
        (False, CalculationStatus.FINAL, "no", None),
        (True, CalculationStatus.PROVISIONAL, "yes", "pays the 8 hours"),
        (
            None,
            CalculationStatus.PROVISIONAL,
            "unconfirmed",
            "does not settle whether the 8 hours",
        ),
    ],
)
def test_hours_apart_decision_and_issue(
    paid_apart: bool | None,
    status: CalculationStatus,
    label: str,
    message: str | None,
) -> None:
    """Even when ordinary hours are owed separately, only EUR 24 is posted."""
    band = next(b for b in _bands() if b.code == "TDS_DOMENICA").model_copy(
        update={"hours_paid_apart": paid_apart}
    )
    event = _sunday()
    terms = _terms(_with_bands((band,)))
    pay = resolve_supplement(event, terms)
    decision = supplement_decision(event, pay, terms)
    issue = supplement_issue(event, pay)

    assert decision.amount == Decimal("24.00")
    assert decision.status is status
    assert decision.inputs["hours_paid_apart"] == label
    if message is None:
        assert issue is None
    else:
        assert issue is not None
        assert issue.code == HOURS_NOT_POSTED
        assert issue.status is CalculationStatus.PROVISIONAL
        assert issue.capability == "holiday_work"
        assert issue.cause is IssueCause.RULE
        assert message in issue.message
        assert "2026-03-15" in issue.message
        assert "10.0000" in issue.message
        assert "supplement only, not those hours" in issue.message


def test_missing_shift_kind_reports_the_fact_and_capability() -> None:
    """An unstated shift kind names the missing input, not merely the amount."""
    with pytest.raises(InvalidInputError) as caught:
        resolve_supplement(ShiftWorkEvent(_DAY, hours=_HOURS), _terms())
    error = caught.value
    assert error.field == "ShiftWorkEvent.kind"
    assert error.feature == "shift_work"
    assert "ShiftWorkEvent.kind is not stated" in str(error)
    assert error.remediation == (
        "Pass ShiftWorkEvent.kind, or ShiftWorkEvent.supplement_amount."
    )
    assert "ShiftWorkEvent.supplement_amount on 2026-03-15" in str(error)


def test_missing_band_reports_the_event_field_and_date() -> None:
    """An absent night band rejects the night amount on the event date."""
    event = NightShiftEvent(_DAY, hours=_HOURS)
    with pytest.raises(MissingRuleError) as caught:
        resolve_supplement(event, _terms(_with_bands(())))
    error = caught.value
    assert error.feature == "night_work"
    assert error.as_of == _DAY
    assert "NightShiftEvent.supplement_amount is not stated" in str(error)
    assert error.remediation == (
        "Pass NightShiftEvent.supplement_amount: the engine does not derive it here."
    )


def test_missing_shift_fact_names_the_input_not_the_amount() -> None:
    """A restricted Sunday band needs the worker's shift status."""
    band = next(b for b in _bands() if b.code == "TDS_DOMENICA").model_copy(
        update={"excludes_periodic_shift": True}
    )
    event = _sunday()
    with pytest.raises(InvalidInputError) as caught:
        resolve_supplement(event, _terms(_with_bands((band,))))
    error = caught.value
    assert error.field == "HolidayWorkEvent.in_periodic_shift"
    assert error.feature == "holiday_work"
    assert "whether the worker is a turnista is not stated" in str(error)
    assert "HolidayWorkEvent.supplement_amount on 2026-03-15" in str(error)
    assert error.remediation == (
        "Pass HolidayWorkEvent.in_periodic_shift, or "
        "HolidayWorkEvent.supplement_amount."
    )


def test_excluded_sunday_band_with_hours_already_paid_has_no_issue() -> None:
    """A shift worker gets zero of the restricted 30%, not a second hour."""
    band = next(b for b in _bands() if b.code == "TDS_DOMENICA").model_copy(
        update={"excludes_periodic_shift": True, "hours_paid_apart": False}
    )
    event = HolidayWorkEvent(
        _DAY, hours=_HOURS, kind=HolidayWorkKind.SUNDAY, in_periodic_shift=True
    )
    terms = _terms(_with_bands((band,)))
    pay = resolve_supplement(event, terms)
    decision = supplement_decision(event, pay, terms)

    assert pay.amount == Decimal("0.00")
    assert decision.status is CalculationStatus.FINAL
    assert decision.inputs["in_periodic_shift"] == "yes"
    assert decision.inputs["hours_paid_apart"] == "no"
    assert supplement_issue(event, pay) is None


def test_unrestricted_night_band_does_not_request_shift_status() -> None:
    """A night band without the shift exclusion has no turnista input."""
    event = NightShiftEvent(_DAY, hours=_HOURS)
    terms = _terms()
    pay = resolve_supplement(event, terms)
    decision = supplement_decision(event, pay, terms)

    assert decision.amount == Decimal("12.00")  # 8 x 15% x EUR 10
    assert decision.inputs["work"] == "night"
    assert "in_periodic_shift" not in decision.inputs
