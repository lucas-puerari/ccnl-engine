"""Every public input validates its fields and collections on construction.

A value of the wrong type, ``NaN``, an infinity, a ``bool`` given as an
``int``, a ``datetime`` given as a ``date`` or a malformed string is
rejected with :class:`~ccnl_engine.InvalidInputError` naming the field, and
an invalid element of a collection is rejected wherever it sits, never
accepted and never surfacing later as ``AttributeError``, ``TypeError`` or
``decimal.InvalidOperation``.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.inputs import (
    Apprentice,
    CalendarOverride,
    CalendarOverrideReason,
    ContributableHours,
    ContributionHistory,
    CurrentYearTaxFacts,
    DeferredShortfall,
    Dependent,
    DependentRelationship,
    EmploymentPeriod,
    FamilyComposition,
    ForeignTaxPaid,
    OpeningBalances,
    PaymentId,
    PayrollRunId,
    PensionFundEnrolment,
    PeriodState,
    Permanent,
    PriorYearTaxFacts,
    RecoveryObligation,
    RecoveryPlan,
    SeniorityFact,
    SenioritySource,
    ShortfallDeferralRequest,
    SubstituteTaxRegime,
    SurtaxComponent,
    SurtaxObligation,
    WeeklyHours,
    WorkCalendar,
)
from tests.integration.ccnl_engine.payroll.family.builders_dependents import (
    declared_dependent,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_YEAR = 2026
_DAY = date(_YEAR, 6, 10)
_ONE = Decimal(1)
_EMPLOYMENT = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    contract_type=Permanent(),
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_OVERTIME = OvertimeEvent(event_date=_DAY, hours=_ONE, hourly_rate=Decimal(15))
_CHILD = declared_dependent(
    relationship=DependentRelationship.CHILD, birth_date=date(2015, 1, 1)
)
_RECOVERY = RecoveryObligation(
    tax_year=_YEAR - 1,
    plan=RecoveryPlan.create("trattamento_integrativo", Decimal(80), 8),
)


def _fields_of(value: object) -> dict[str, Any]:
    return {f.name: getattr(value, f.name) for f in dataclasses.fields(value)}  # type: ignore[arg-type]


#: Valid keyword arguments of each public input, one field at a time
#: replaced by an invalid value below.
_VALID: dict[type, dict[str, Any]] = {
    OvertimeEvent: {"event_date": _DAY, "hours": _ONE, "hourly_rate": _ONE},
    NightShiftEvent: {"event_date": _DAY, "supplement_amount": _ONE},
    HolidayWorkEvent: {"event_date": _DAY, "supplement_amount": _ONE},
    ShiftWorkEvent: {"event_date": _DAY, "supplement_amount": _ONE},
    AbsenceEvent: {"event_date": _DAY, "hours": _ONE, "hourly_rate": _ONE},
    SickLeaveEvent: {"event_date": _DAY, "amount": _ONE},
    BonusEvent: {"event_date": _DAY, "amount": _ONE},
    FringeEvent: {"event_date": _DAY, "amount": _ONE},
    WelfareEvent: {"event_date": _DAY, "amount": _ONE},
    ArrearsEvent: {
        "event_date": _DAY,
        "amount": _ONE,
        "separate_tax_rate": Decimal("0.2"),
    },
    BilateralFundEvent: {
        "event_date": _DAY,
        "employee_amount": _ONE,
        "employer_amount": _ONE,
    },
    TerminationTFREvent: {
        "event_date": _DAY,
        "amount": _ONE,
        "separate_tax_rate": Decimal("0.2"),
    },
    Employment: {
        "ccnl_slug": "metalmeccanico-federmeccanica.json",
        "level_code": "C3",
        "contract_type": Permanent(),
    },
    Apprentice: {"months_elapsed": 1},
    EmployerProfile: {"headcount": Headcount(5)},
    Headcount: {"value": 5},
    WeeklyHours: {"value": 40},
    ContributableHours: {"value": _ONE},
    EmploymentPeriod: {"started_on": _DAY},
    SeniorityFact: {"months": 1, "as_of": _DAY, "source": SenioritySource.PAYSLIP},
    ContributionHistory: {"first_enrolled_on": _DAY},
    PensionFundEnrolment: {
        "fund_code": "ALIFOND",
        "employee_rate": Decimal("0.01"),
        "tfr_to_fund": True,
    },
    Dependent: {
        "relationship": DependentRelationship.SPOUSE,
        "dependent_from": None,
        "dependent_until": None,
    },
    FamilyComposition: {},
    ForeignTaxPaid: {"country": "FR", "income": _ONE, "tax": _ONE},
    ShortfallDeferralRequest: {"signed_on": _DAY},
    PriorYearTaxFacts: {},
    CurrentYearTaxFacts: {
        "tax_year": _YEAR,
        "other_employment_income": _ONE,
        "other_employment_inps_base": _ONE,
        "other_income": _ONE,
        "main_dwelling_income": _ONE,
        "exempt_regime_income": _ONE,
        "estimated_on": _DAY,
        "quality": "declared",
    },
    PeriodFacts: {},
    PayrollRun: {"run_kind": "regular", "month": 6, "year": _YEAR},
    PayrollRunId: {"year": _YEAR, "month": 6, "kind": "regular"},
    PaymentId: {
        "run_id": PayrollRunId.parse(f"{_YEAR}-06-regular"),
        "payment_date": date(_YEAR, 6, 27),
    },
    WorkCalendar: {"year": _YEAR},
    CalendarOverride: {
        "calendar": WorkCalendar(year=_YEAR),
        "reason": CalendarOverrideReason.PAYMENT_MONTH,
        "note": "CCNL art. 1",
    },
    RecoveryPlan: {
        "kind": "trattamento_integrativo",
        "original_amount": Decimal(80),
        "installment_amount": Decimal(10),
        "installments_total": 8,
        "installments_posted": 0,
    },
    RecoveryObligation: {"tax_year": _YEAR - 1, "plan": _RECOVERY.plan},
    OpeningBalances: {
        "tax_year": _YEAR,
        "inps_bases": (),
        "recoveries": (),
        "surtax_obligations": (),
    },
    PeriodState: {},
    PeriodInput: {
        "run": PayrollRun.regular(_YEAR, 6),
        "payment_date": date(_YEAR, 6, 27),
        "employment": _EMPLOYMENT,
        "employer": _EMPLOYER,
    },
    CompetenceYearPlan: {
        "year": _YEAR,
        "employment": _EMPLOYMENT,
        "employer": _EMPLOYER,
    },
    DeferredShortfall: {
        "tax_year": _YEAR - 1,
        "signed_on": date(_YEAR, 1, 20),
        "deferred_from": date(_YEAR, 1, 1),
        "irpef": Decimal(100),
    },
    SurtaxObligation: _fields_of(
        SurtaxObligation.open(
            SurtaxComponent.REGIONAL_BALANCE, _YEAR - 1, "IT-45", _ONE
        )
    ),
}

#: Values no field of a public input accepts in place of its own type,
#: unless the field is optional (``None``) or a bool (``True``).
_INVALID: tuple[object, ...] = (
    Decimal("NaN"),
    Decimal("sNaN"),
    Decimal("Infinity"),
    Decimal("-Infinity"),
    Decimal("1E+12"),
    True,
    1.5,
    float("nan"),
    "",
    "not a value",
    datetime(_YEAR, 6, 10, 9, 0),  # noqa: DTZ001
    None,
    object(),
    [object()],
)

_CASES = [(cls, f.name) for cls in _VALID for f in dataclasses.fields(cls) if f.init]


def _build(cls: type, field: str, value: object) -> object:
    """Build ``cls`` with ``field`` replaced by ``value``.

    Returns:
        The input, or the ``InvalidInputError`` it raised.
    """
    try:
        return cls(**{**_VALID[cls], field: value})
    except InvalidInputError as error:
        return error


def test_every_valid_input_constructs() -> None:
    """The valid arguments above build every input: the baseline is sound."""
    for cls, kwargs in _VALID.items():
        assert isinstance(cls(**kwargs), cls)


@pytest.mark.parametrize(
    ("cls", "field"), _CASES, ids=lambda v: getattr(v, "__name__", v)
)
@pytest.mark.parametrize("value", _INVALID, ids=repr)
def test_an_invalid_scalar_is_rejected_with_its_field(
    cls: type, field: str, value: object
) -> None:
    """Either the value is a valid one for the field, or the input names it.

    No other exception than ``InvalidInputError`` is ever raised.
    """
    outcome = _build(cls, field, value)

    if isinstance(outcome, InvalidInputError):
        assert outcome.field is not None
        assert outcome.field.split(".")[0] == cls.__name__
        assert outcome.remediation is not None
    else:
        assert getattr(outcome, field) == value or value in {None, True}


def _positions(size: int) -> st.SearchStrategy[int]:
    return st.integers(min_value=0, max_value=size)


_BAD_ELEMENTS = st.sampled_from([None, object(), "x", Decimal(1), 1, True])


def _check_position(
    build: Callable[[list[object]], object],
    valid: list[object],
    index: int,
    bad: object,
    field: str,
) -> None:
    elements = [*valid[:index], bad, *valid[index:]]
    with pytest.raises(InvalidInputError) as raised:
        build(elements)
    assert raised.value.field == f"{field}[{index}]"


@given(index=_positions(3), bad=_BAD_ELEMENTS)
def test_an_invalid_event_is_rejected_at_any_position(index: int, bad: object) -> None:
    """First, middle or last: the event is named by its position."""
    valid: list[object] = [_OVERTIME] * 3
    _check_position(
        lambda e: PeriodFacts(events=e),  # type: ignore[arg-type]
        valid,
        index,
        bad,
        "PeriodFacts.events",
    )


@given(index=_positions(2), bad=_BAD_ELEMENTS)
def test_an_invalid_dependent_is_rejected_at_any_position(
    index: int, bad: object
) -> None:
    """A dependent that is not a :class:`Dependent` is named by its position."""
    _check_position(
        lambda d: FamilyComposition(dependents=d),  # type: ignore[arg-type]
        [_CHILD, _CHILD],
        index,
        bad,
        "FamilyComposition.dependents",
    )


@given(index=_positions(2), bad=_BAD_ELEMENTS)
def test_an_invalid_foreign_tax_is_rejected_at_any_position(
    index: int, bad: object
) -> None:
    """A foreign tax that is not a :class:`ForeignTaxPaid` is named."""
    taxes: list[object] = [
        ForeignTaxPaid(country=c, income=_ONE, tax=_ONE) for c in ("FR", "DE")
    ]
    _check_position(
        lambda t: PriorYearTaxFacts(foreign_taxes=t),  # type: ignore[arg-type]
        taxes,
        index,
        bad,
        "PriorYearTaxFacts.foreign_taxes",
    )


@given(index=_positions(2), bad=_BAD_ELEMENTS)
def test_an_invalid_opening_recovery_is_rejected_at_any_position(
    index: int, bad: object
) -> None:
    """An imported recovery that is not a :class:`RecoveryObligation`."""
    recoveries: list[object] = [_RECOVERY, _RECOVERY]
    _check_position(
        lambda r: OpeningBalances(
            tax_year=_YEAR,
            recoveries=r,  # type: ignore[arg-type]
            inps_bases=(),
            surtax_obligations=(),
        ),
        recoveries,
        index,
        bad,
        "OpeningBalances.recoveries",
    )


@given(month=st.integers(min_value=1, max_value=12), bad=_BAD_ELEMENTS)
def test_invalid_facts_of_any_month_are_rejected(month: int, bad: object) -> None:
    """A value of :attr:`CompetenceYearPlan.periods` that is not facts names its key."""
    periods: dict[object, object] = dict.fromkeys(range(1, 13), PeriodFacts())
    periods[month] = bad
    with pytest.raises(InvalidInputError) as raised:
        CompetenceYearPlan(
            year=_YEAR,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            periods=periods,  # type: ignore[arg-type]
        )
    assert raised.value.field == f"CompetenceYearPlan.periods[{month}]"


@pytest.mark.parametrize("bad", [1, "", None, True], ids=repr)
def test_an_invalid_role_or_waiver_is_rejected(bad: object) -> None:
    """Elements of a frozenset are checked like those of a tuple."""
    roles: frozenset[object] = frozenset({"capoturno", bad})
    with pytest.raises(InvalidInputError, match=r"Employment\.roles\["):
        dataclasses.replace(_EMPLOYMENT, roles=roles)  # type: ignore[arg-type]
    with pytest.raises(InvalidInputError, match=r"PriorYearTaxFacts\.waived_regimes\["):
        PriorYearTaxFacts(
            waived_regimes=frozenset({SubstituteTaxRegime.RINNOVO, bad})  # type: ignore[arg-type]
        )


def test_lists_are_normalised_to_tuples_after_validation() -> None:
    """A list of events, dependents or extra months is stored as a tuple."""
    assert PeriodFacts(events=[_OVERTIME]).events == (_OVERTIME,)  # type: ignore[arg-type]
    family = FamilyComposition(dependents=[_CHILD])  # type: ignore[arg-type]
    assert family.dependents == (_CHILD,)
    balances = OpeningBalances(
        tax_year=_YEAR,
        recoveries=[_RECOVERY],  # type: ignore[arg-type]
        inps_bases=(),
        surtax_obligations=(),
    )
    assert balances.recoveries == (_RECOVERY,)
