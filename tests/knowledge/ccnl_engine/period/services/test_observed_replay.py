"""Observed payslips replayed through the public API of the engine.

Each record of ``observed_payslip/`` states in ``replay`` whether it can be
replayed, ``full``, ``partial`` or ``not_replayable``, under the rules of
:mod:`scripts.provenance.replay.check`: a partial replay names each fact
the request cannot state and what it affects, and compares nothing an
unknown fact can move.

A replayable record builds its request from the observed facts alone
(``inputs``) and pins each value it compares in ``expected``, with the field
of the payslip it was read from and a tolerance.  A difference fails unless
``known_differences`` lists it with its reason, its owner and the date
until which it is accepted: a new divergence never passes silently, and an
accepted one expires.  The runner computes nothing itself; it reads the
result of :meth:`~ccnl_engine.PayrollEngine.calculate_period`.
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.event import facade as event_facade
from ccnl_engine.event.facade import OvertimeKind, StandbyKind
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    EmploymentPeriod,
    FixedTerm,
    NoPensionFund,
    PensionFundEnrolment,
    Permanent,
    PriorYearTaxFacts,
    PublicEndOfService,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
    WorkerCategory,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.run.types import PeriodId
from scripts.provenance.replay.check import (
    EVENT_TYPES,
    INPUT_KEYS,
    REPLAY_KEYS,
    load_records,
    record_errors,
    replay_errors,
)
from tests.knowledge.ccnl_engine.period.sector.test_services import _year

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine import PeriodResult

_RECORDS = load_records()
_ENGINE = PayrollEngine.bundled()
#: Day the accepted differences are checked against.
_TODAY = datetime.now(tz=UTC).date()
_ZERO = Decimal(0)


def _items(kind: str) -> Callable[[PeriodResult], Decimal]:
    def read(result: PeriodResult) -> Decimal:
        return sum((i.amount for i in result.pay_items if i.kind == kind), _ZERO)

    return read


def _accounts(
    *plus: AccountKind, minus: tuple[AccountKind, ...] = ()
) -> Callable[[PeriodResult], Decimal]:
    def read(result: PeriodResult) -> Decimal:
        def total(kinds: tuple[AccountKind, ...]) -> Decimal:
            return sum(
                (e.amount for e in result.ledger_entries if e.account in kinds), _ZERO
            )

        return total(plus) - total(minus)

    return read


def _inps_rate(side: str) -> Callable[[PeriodResult], Decimal]:
    def read(result: PeriodResult) -> Decimal:
        components = result.contribution_breakdown.components
        return sum((c.rate for c in components if c.name.endswith(side)), _ZERO)

    return read


def _inps_base(result: PeriodResult) -> Decimal:
    components = result.contribution_breakdown.components
    return next((c.base for c in components if c.name == "ivs_employee"), _ZERO)


def _annual_tax(*names: str) -> Callable[[PeriodResult], Decimal]:
    def read(result: PeriodResult) -> Decimal:
        lines = result.tax_computation.components
        return sum((c.amount for c in lines if c.name in names), _ZERO)

    return read


def _ytd_taxable(result: PeriodResult) -> Decimal:
    return result.closing_state.cash.earnings.taxable


_A = AccountKind
#: Taxes withheld in the run net of the refunds, before any credit: the
#: tax accounts of the net identity of the engine.
_TAX = _accounts(
    _A.ORDINARY_TAX,
    _A.SURTAX,
    _A.SUBSTITUTE_TAX,
    _A.SEPARATE_TAX,
    minus=(_A.TAX_REFUNDS, _A.SURTAX_REFUNDS),
)
#: Credits paid in the run net of those taken back.
_CREDITS = _accounts(
    _A.CREDITS, _A.CREDIT_RECOVERY_SHORTFALL, minus=(_A.CREDIT_RECOVERIES,)
)
#: How the result gives each value a record can compare; its axis, a total,
#: a component or a rate, is :data:`~scripts.provenance.reference_case.check.AXIS_OF`.
_READERS: dict[str, Callable[[PeriodResult], Decimal]] = {
    "base_salary": _items("base_salary_earning"),
    "period_gross": lambda r: r.period_gross,
    "employee_contributions": _accounts(_A.EMPLOYEE_CONTRIBUTIONS),
    "employer_contributions": _accounts(_A.EMPLOYER_CONTRIBUTIONS),
    "period_tax": _TAX,
    "period_net": lambda r: r.period_net,
    "tfr_accrual": _accounts(_A.TFR_ACCRUAL, _A.PENSION_FUND_TFR, _A.TFR_TREASURY_FUND),
    "employer_cost": lambda r: r.period_employer_cost,
    "fixed_allowances": _items("fixed_allowance_earning"),
    "inps_base": _inps_base,
    "ytd_taxable_income": _ytd_taxable,
    "annual_gross_irpef": _annual_tax("irpef_gross"),
    "annual_tax_deductions": _annual_tax(
        "work_deduction", "family_deductions", "ulteriore_detrazione"
    ),
    "period_tax_credits": _CREDITS,
    "period_surtax": _accounts(_A.SURTAX, minus=(_A.SURTAX_REFUNDS,)),
    "employee_funds": _accounts(_A.PENSION_FUND_EMPLOYEE, _A.BILATERAL_FUND_EMPLOYEE),
    "employer_funds": _accounts(_A.PENSION_FUND_EMPLOYER, _A.BILATERAL_FUND_EMPLOYER),
    "employee_inps_rate": _inps_rate("_employee"),
    "employer_inps_rate": _inps_rate("_employer"),
}


def _replayable() -> list[str]:
    return [
        pid
        for pid, r in _RECORDS.items()
        if r["replay"]["replayability"] != "not_replayable"
    ]


def _seniority(inputs: dict[str, Any]) -> SeniorityFact | None:
    months, as_of = inputs.get("seniority_months"), inputs.get("seniority_as_of")
    if months is None or as_of is None:
        return None
    return SeniorityFact(
        int(months), date.fromisoformat(as_of), SenioritySource.PAYSLIP
    )


def _pension_fund(
    inputs: dict[str, Any],
) -> PensionFundEnrolment | NoPensionFund | None:
    fund = inputs.get("pension_fund")
    if fund is None:
        return None
    if fund == "none":
        return NoPensionFund()
    return PensionFundEnrolment(
        fund_code=fund["fund_code"],
        employee_rate=Decimal(fund["employee_rate"]),
        tfr_to_fund=bool(fund["tfr_to_fund"]),
    )


def _employment(inputs: dict[str, Any]) -> Employment:
    hired, ended = inputs.get("hired_on"), inputs.get("terminated_on")
    hours, full_time = inputs.get("weekly_hours"), inputs.get("full_time_weekly_hours")
    category, regime = inputs.get("category"), inputs.get("public_end_of_service")
    return Employment(
        ccnl_id=inputs["ccnl_id"],
        level_code=inputs["level_code"],
        contract_type=FixedTerm()
        if inputs["contract_type"] == "fixed_term"
        else Permanent(),
        category=None if category is None else WorkerCategory(category),
        employment_period=None
        if hired is None
        else EmploymentPeriod(
            date.fromisoformat(hired),
            None if ended is None else date.fromisoformat(ended),
        ),
        weekly_hours=None if hours is None else WeeklyHours(Decimal(hours)),
        full_time_weekly_hours=None
        if full_time is None
        else WeeklyHours(Decimal(full_time)),
        seniority=_seniority(inputs),
        pension_fund=_pension_fund(inputs),
        tfr_treasury_fund=inputs.get("tfr_treasury_fund"),
        public_end_of_service=None if regime is None else PublicEndOfService(regime),
    )


def _field(annotation: str, value: object) -> object:
    """Return ``value`` as the type its event field declares.

    Returns:
        The converted value, ``None`` for an unstated optional field.

    Raises:
        TypeError: For a field type the replay does not state.
    """
    kind = annotation.removesuffix(" | None")
    if value is None:
        return None
    converters: dict[str, Callable[[Any], object]] = {
        "date": date.fromisoformat,
        "Decimal": lambda v: Decimal(str(v)),
        "int": int,
        "bool": bool,
        "OvertimeKind": OvertimeKind,
        "StandbyKind": StandbyKind,
        "PeriodId": lambda v: PeriodId(year=int(v[:4]), month=int(v[5:7])),
    }
    if kind.startswith("Literal["):
        return str(value)
    if kind not in converters:
        msg = f"event field type {annotation!r} has no replay converter"
        raise TypeError(msg)
    return converters[kind](value)


def _event(spec: dict[str, Any]) -> object:
    """Build one event of a record from its stated fields alone.

    Returns:
        The event.

    Raises:
        TypeError: For a field the event does not have.
    """
    cls = getattr(event_facade, spec["type"])
    declared = {f.name: f.type for f in dataclasses.fields(cls) if f.init}
    stated = {k: v for k, v in spec.items() if k != "type"}
    unknown = set(stated) - set(declared)
    if unknown:
        msg = f"{spec['type']} has no field {sorted(unknown)}"
        raise TypeError(msg)
    return cls(**{k: _field(str(declared[k]), v) for k, v in stated.items()})


_RUNS = {
    "regular": PayrollRun.regular,
    "thirteenth": PayrollRun.thirteenth,
    "fourteenth": PayrollRun.fourteenth,
}


def _request(inputs: dict[str, Any]) -> PeriodInput:
    """Build the request of a record from its observed facts alone.

    Returns:
        The request; a fact the record does not state keeps its default.
    """
    year, month = int(inputs["year"]), int(inputs["month"])
    income = inputs.get("prior_year_employment_income")
    estimated = inputs.get("current_year_employment_only_on")
    return PeriodInput(
        run=_RUNS[inputs.get("run_kind", "regular")](year, month),
        payment_date=date(year, month, 27),
        employment=_employment(inputs),
        employer=EmployerProfile(
            headcount=Headcount(int(inputs["headcount"])),
            public_life_insurance=inputs.get("public_life_insurance"),
        ),
        facts=PeriodFacts(
            regione=inputs.get("regione"),
            comune_belfiore=inputs.get("comune_belfiore"),
            events=tuple(_event(e) for e in inputs.get("events", [])),  # type: ignore[misc]
        ),
        prior_year=PriorYearTaxFacts(
            employment_income=None if income is None else Decimal(income)
        ),
        current_year=None
        if estimated is None
        else CurrentYearTaxFacts.employment_only(year, date.fromisoformat(estimated)),
    )


def _run(inputs: dict[str, Any]) -> PeriodResult:
    return _ENGINE.calculate_period(_request(inputs))


_EVERY_INPUT: dict[str, Any] = {
    "ccnl_id": "metalmeccanico-federmeccanica",
    "level_code": "C3",
    "year": 2026,
    "month": 12,
    "headcount": 20,
    "contract_type": "fixed_term",
    "category": "impiegato",
    "public_life_insurance": False,
    "hired_on": "2024-03-01",
    "terminated_on": "2026-12-31",
    "weekly_hours": 30,
    "full_time_weekly_hours": 40,
    "regione": "IT-34",
    "comune_belfiore": "L736",
    "prior_year_employment_income": "28000.00",
    "tfr_treasury_fund": True,
    "public_end_of_service": "tfr_employer",
    "run_kind": "thirteenth",
    "seniority_months": 33,
    "seniority_as_of": "2026-12-01",
    "pension_fund": {
        "fund_code": "cometa",
        "employee_rate": "0.012",
        "tfr_to_fund": False,
    },
    "current_year_employment_only_on": "2026-12-01",
    "events": [
        {
            "type": "OvertimeEvent",
            "event_date": "2026-12-10",
            "hours": "4",
            "hourly_rate": "15.00",
            "multiplier": "1.25",
            "kind": "weekday",
        }
    ],
}
#: One event of each type a record may state, with every field it accepts.
_EVENTS: list[dict[str, Any]] = [
    {
        "type": "AbsenceEvent",
        "event_date": "2026-03-02",
        "hours": "8",
        "hourly_rate": "12.50",
        "end_date": "2026-03-02",
        "suspends_accrual": False,
        "no_pay_due": None,
    },
    {
        "type": "OvertimeEvent",
        "event_date": "2026-03-03",
        "hours": "2",
        "hourly_rate": "15.00",
        "multiplier": None,
        "kind": "weekday",
    },
    {
        "type": "NightShiftEvent",
        "event_date": "2026-03-04",
        "supplement_amount": "40.00",
    },
    {
        "type": "HolidayWorkEvent",
        "event_date": "2026-03-05",
        "supplement_amount": "30.00",
    },
    {
        "type": "ShiftWorkEvent",
        "event_date": "2026-03-06",
        "supplement_amount": "20.00",
    },
    {
        "type": "StandbyEvent",
        "event_date": "2026-03-07",
        "kind": "worked_day",
        "quantity": "1",
        "calls": 0,
    },
    {
        "type": "BonusEvent",
        "event_date": "2026-03-08",
        "amount": "500.00",
        "kind": "contract_renewal",
        "agreement_signed_on": "2025-06-01",
    },
    {"type": "FringeEvent", "event_date": "2026-03-09", "amount": "100.00"},
    {"type": "WelfareEvent", "event_date": "2026-03-10", "amount": "200.00"},
    {
        "type": "ArrearsEvent",
        "event_date": "2026-03-11",
        "amount": "300.00",
        "separate_tax_rate": "0.23",
        "reference_period": "2025-06",
    },
    {
        "type": "BilateralFundEvent",
        "event_date": "2026-03-12",
        "employee_amount": "5.00",
        "employer_amount": "10.00",
    },
    {
        "type": "TravelAllowanceEvent",
        "event_date": "2026-03-13",
        "days": 2,
        "outside_municipality": True,
        "meals_lodging": "none",
        "daily_amount": "50.00",
        "hours_away": "10",
        "tfr_base": "none",
        "abroad": False,
        "trasfertista": False,
    },
]


def test_every_event_type_of_the_checker_is_built_with_its_fields() -> None:
    """Each event a record may state reaches the request with its stated fields."""
    built = [_event(spec) for spec in _EVENTS]

    assert {spec["type"] for spec in _EVENTS} == EVENT_TYPES
    for spec, event in zip(_EVENTS, built, strict=True):
        assert type(event).__name__ == spec["type"]
        assert dataclasses.asdict(event)["event_date"] == date.fromisoformat(  # type: ignore[call-overload]
            spec["event_date"]
        )
    arrears = built[9]
    assert isinstance(arrears, event_facade.ArrearsEvent)
    assert arrears.reference_period == PeriodId(year=2025, month=6)
    assert arrears.separate_tax_rate == Decimal("0.23")


def test_an_event_field_the_engine_lacks_is_rejected() -> None:
    """A record cannot slip an override into an event."""
    with pytest.raises(TypeError, match="has no field"):
        _event({
            "type": "BonusEvent",
            "event_date": "2026-03-08",
            "amount": "1",
            "period_net": "9",
        })


def test_every_input_of_the_checker_reaches_the_request() -> None:
    """Each fact a record may state is carried into the request as stated."""
    request = _request(_EVERY_INPUT)
    employment = request.employment

    assert set(_EVERY_INPUT) == INPUT_KEYS
    assert (request.run.run_kind.value, request.run.year, request.run.month) == (
        "thirteenth",
        2026,
        12,
    )
    assert isinstance(employment.contract_type, FixedTerm)
    assert employment.category is WorkerCategory.IMPIEGATO
    assert employment.employment_period == EmploymentPeriod(
        date(2024, 3, 1), date(2026, 12, 31)
    )
    assert (employment.weekly_hours, employment.full_time_weekly_hours) == (
        WeeklyHours(Decimal(30)),
        WeeklyHours(Decimal(40)),
    )
    assert employment.seniority == SeniorityFact(
        33, date(2026, 12, 1), SenioritySource.PAYSLIP
    )
    assert employment.pension_fund == PensionFundEnrolment(
        fund_code="cometa", employee_rate=Decimal("0.012"), tfr_to_fund=False
    )
    assert employment.tfr_treasury_fund is True
    assert employment.public_end_of_service is PublicEndOfService.TFR_EMPLOYER
    assert request.employer.headcount == Headcount(20)
    assert request.employer.public_life_insurance is False
    assert (request.facts.regione, request.facts.comune_belfiore) == ("IT-34", "L736")
    assert request.prior_year.employment_income == Decimal("28000.00")
    assert request.current_year == CurrentYearTaxFacts.employment_only(
        2026, date(2026, 12, 1)
    )
    (overtime,) = request.facts.events
    assert overtime == event_facade.OvertimeEvent(
        date(2026, 12, 10),
        Decimal(4),
        Decimal("15.00"),
        Decimal("1.25"),
        OvertimeKind.WEEKDAY,
    )
    assert record_errors_of(_EVERY_INPUT) == []


def record_errors_of(inputs: dict[str, Any]) -> list[str]:
    """Return the checker errors of a partial replay built on ``inputs``.

    Returns:
        The messages of :func:`~scripts.provenance.replay.check.replay_errors`.
    """
    replay = {
        "replayability": "partial",
        "reason": "synthetic",
        "inputs": inputs,
        "unknown_inputs": [{"input": "superminimo", "affects": ["gross"]}],
        "expected": {"base_salary": {"printed": "x", "value": "1", "tolerance": "0"}},
        "known_differences": [],
    }
    return replay_errors(replay, _TODAY)


def test_a_record_without_a_pension_fund_states_none() -> None:
    """``"none"`` is the worker without a complementary fund."""
    assert _request(
        _EVERY_INPUT | {"pension_fund": "none"}
    ).employment.pension_fund == (NoPensionFund())


def test_every_record_follows_the_replay_rules() -> None:
    """No record compares a value an unknown fact can move, or has no reader."""
    assert record_errors(_TODAY) == []


def test_every_replay_key_has_a_reader() -> None:
    """A key the checker allows is one the runner can read, and no other."""
    assert set(_READERS) == REPLAY_KEYS


@pytest.mark.parametrize("pid", _replayable())
def test_the_engine_reproduces_the_observed_values(pid: str) -> None:
    """Each compared value is within its tolerance, or a listed difference."""
    replay = _RECORDS[pid]["replay"]
    result = _run(replay["inputs"])
    known = {d["key"] for d in replay["known_differences"]}

    diff = {
        key: (_READERS[key](result), Decimal(spec["value"]))
        for key, spec in replay["expected"].items()
        if abs(_READERS[key](result) - Decimal(spec["value"]))
        > Decimal(spec["tolerance"])
    }

    assert set(diff) == known, diff


def test_the_replayable_records_cover_the_sectors_of_the_production_ccnls() -> None:
    """Payslips of 2026 of five CCNLs, private and public, are replayed."""
    ccnls = {_RECORDS[pid]["replay"]["inputs"]["ccnl_id"] for pid in _replayable()}

    assert len(_replayable()) >= 11
    assert ccnls == {
        "commercio-confcommercio",
        "edilizia-ance",
        "funzioni-locali-aran",
        "industria-turistica-federturismo",
        "metalmeccanico-federmeccanica",
    }


def _terminated() -> PeriodResult:
    """Return the termination run of the edilizia oracle.

    Returns:
        A run that posts every account a reader sums.
    """
    return _year("edilizia-june").period_results[-1]


def test_the_total_readers_read_the_totals_of_the_result() -> None:
    """Contributions, tax and net agree with the breakdowns of the run."""
    result = _terminated()
    read = {key: reader(result) for key, reader in _READERS.items()}
    breakdown = result.contribution_breakdown

    assert read["period_gross"] == result.period_gross > _ZERO
    assert read["employee_contributions"] == breakdown.employee > _ZERO
    assert read["period_surtax"] > _ZERO
    assert read["period_tax"] > read["period_surtax"]
    assert read["tfr_accrual"] > _ZERO
    assert read["employer_funds"] > _ZERO
    assert read["employer_cost"] == result.period_employer_cost > read["period_gross"]


def test_the_tax_and_net_readers_reconcile_with_the_net_identity() -> None:
    """Net = cash + credits + TFR paid - contributions - funds - deductions - tax."""
    result = _terminated()
    read = {key: reader(result) for key, reader in _READERS.items()}
    rest = _accounts(
        _A.CASH_EARNINGS,
        _A.TFR_SETTLEMENT,
        minus=(_A.EMPLOYEE_DEDUCTIONS,),
    )(result)

    assert read["period_net"] == (
        rest
        + read["period_tax_credits"]
        - read["employee_contributions"]
        - read["employee_funds"]
        - read["period_tax"]
    )


def test_bases_and_amounts_are_read_apart_from_the_rates() -> None:
    """The base and the amount are money; the rate is their ratio, to the cent."""
    result = _terminated()
    base, rate = _READERS["inps_base"](result), _READERS["employee_inps_rate"](result)
    amount = _READERS["employee_contributions"](result)

    assert base == base.quantize(Decimal(1)) > _ZERO
    assert Decimal(0) < rate < Decimal("0.2")
    assert abs(amount - base * rate) <= Decimal("0.02")
    assert _READERS["employer_inps_rate"](result) > rate


def test_the_annual_tax_readers_read_the_year_of_the_conguaglio() -> None:
    """Gross IRPEF and deductions are annual amounts; the taxable is the YTD."""
    result = _terminated()

    assert _READERS["annual_gross_irpef"](result) > _ZERO
    assert _READERS["annual_tax_deductions"](result) > _ZERO
    assert _READERS["ytd_taxable_income"](result) > result.period_gross
