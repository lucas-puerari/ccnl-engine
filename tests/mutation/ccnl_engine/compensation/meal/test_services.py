"""Daily contractual meal benefits on caller-verified eligible days."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

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
from ccnl_engine.compensation.meal.services import meal_benefit, meal_benefit_issue
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WorkerCategory
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.run.types import RunKind
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext


def _run(
    *,
    year: int,
    month: int,
    days: int | None,
    headcount: int = 11,
    level: str = "4",
    ccnl_id: str = "ced-assoced",
    run: PayrollRun | None = None,
    started_on: date | None = None,
    ended_on: date | None = None,
) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=run or PayrollRun.regular(year=year, month=month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                category=(
                    WorkerCategory.QUADRO
                    if level in {"Q", "QDIR"}
                    else WorkerCategory.IMPIEGATO
                ),
                seniority=new_hire(year),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(
                    started_on or date(year, month, 1), ended_on
                ),
            ),
            employer=EmployerProfile(headcount=Headcount(headcount)),
            facts=PeriodFacts(
                meal_benefit_days=days, regione="IT-25", comune_belfiore="A005"
            ),
        )
    )


def test_daily_meal_benefit_2026() -> None:
    """October 2026: 20 eligible days * EUR 8 = EUR 160, versus EUR 0 undeclared."""
    before = _run(year=2026, month=10, days=None)
    after = _run(year=2026, month=10, days=20)
    welfare = [item for item in after.pay_items if item.kind == "welfare_item"]
    assert sum((item.amount for item in welfare), Decimal(0)) == Decimal("160.00")
    assert not [item for item in before.pay_items if item.kind == "welfare_item"]
    assert after.period_gross == before.period_gross


@pytest.mark.parametrize(("level", "fixed"), [("Q", "258.00"), ("QDIR", "296.00")])
def test_existing_fixed_allowance_and_daily_benefit(level: str, fixed: str) -> None:
    """October 2026: Q/QDIR fixed EUR 258/296 plus 10 days * EUR 8 = EUR 80."""
    result = _run(year=2026, month=10, days=10, level=level)
    assert sum(
        (i.amount for i in result.pay_items if "INDENNITA_FUNZIONE" in i.item_id),
        Decimal(0),
    ) == Decimal(fixed)
    assert sum(
        (i.amount for i in result.pay_items if i.kind == "welfare_item"),
        Decimal(0),
    ) == Decimal("80.00")


def test_daily_rate_change_is_dated() -> None:
    """The 2022 daily EUR 6 becomes EUR 8 on 1 September 2025."""
    ccnl = BundledKnowledgeRepository().load_ccnl("ced-assoced")
    rates = ccnl.parameters.meal_benefit_daily
    assert rates is not None
    assert rates.value_at(date(2025, 8, 31)) == Decimal("6.00")
    assert rates.value_at(date(2025, 9, 1)) == Decimal("8.00")
    renewed = rates.period_at(date(2025, 9, 1))
    assert renewed is not None
    assert renewed.provenance is not None
    location = renewed.provenance.location
    assert location is not None
    assert location.page == "32"
    assert location.source_document.sha256 == (
        "e197c24e9028d8f0924893d9bab708107b1ffb015d963ee06c8c2ddbe87a772e"
    )


def test_unknown_days_before_dated_rate_do_not_raise_issue() -> None:
    """Before the first EUR 6 rate there is no EUR 6 or EUR 8 entitlement."""
    ccnl = BundledKnowledgeRepository().load_ccnl("ced-assoced")
    ctx = cast(
        "RunContext",
        SimpleNamespace(
            request=SimpleNamespace(
                meal_benefit_days=None,
                employer=EmployerProfile(headcount=Headcount(11)),
                run=PayrollRun.regular(2022, 1),
            ),
            contract=SimpleNamespace(
                ccnl=ccnl, tctx=SimpleNamespace(competence=date(2022, 1, 1))
            ),
        ),
    )
    assert meal_benefit_issue(ctx) is None


def test_direct_request_without_employment_span_can_post() -> None:
    """Without a tracked span, 1 verified day * EUR 8 posts EUR 8."""
    ccnl = BundledKnowledgeRepository().load_ccnl("ced-assoced")
    ctx = cast(
        "RunContext",
        SimpleNamespace(
            request=SimpleNamespace(
                meal_benefit_days=1,
                employer=EmployerProfile(headcount=Headcount(11)),
                run=PayrollRun.regular(2026, 10),
                employment_period=None,
            ),
            contract=SimpleNamespace(
                ccnl=ccnl, tctx=SimpleNamespace(competence=date(2026, 10, 1))
            ),
        ),
    )
    assert meal_benefit(ctx)[0].amount == Decimal("8.00")


def test_declared_days_without_employed_span_are_rejected() -> None:
    """No employed October days cannot earn EUR 8 * 1 = EUR 8."""
    ccnl = BundledKnowledgeRepository().load_ccnl("ced-assoced")
    ctx = cast(
        "RunContext",
        SimpleNamespace(
            request=SimpleNamespace(
                meal_benefit_days=1,
                employer=EmployerProfile(headcount=Headcount(11)),
                run=PayrollRun.regular(2026, 10),
                employment_period=SimpleNamespace(span_in_month=lambda _y, _m: None),
            ),
            contract=SimpleNamespace(
                ccnl=ccnl, tctx=SimpleNamespace(competence=date(2026, 10, 1))
            ),
        ),
    )
    with pytest.raises(InvalidInputError, match="exceeds employed days"):
        meal_benefit(ctx)


def test_meal_benefit_does_not_guess_eligible_days() -> None:
    """Unverified and zero-day months both pay EUR 0.

    Only the unknown count blocks the calculation.
    """
    for days in (None, 0):
        result = _run(year=2026, month=1, days=days)
        assert not [i for i in result.pay_items if i.kind == "welfare_item"]
        issues = [i for i in result.issues if i.fact == "meal_benefit_days"]
        assert len(issues) == (1 if days is None else 0)
        if days is None:
            assert issues[0].status == CalculationStatus.INCOMPLETE
            assert any(
                b.code == "missing_fact" and b.detail == "meal_benefit_days"
                for b in result.blockers
            )


@pytest.mark.parametrize(
    ("headcount", "ccnl_id", "run"),
    [
        (10, "ced-assoced", None),
        (11, "commercio-confcommercio", None),
        (11, "ced-assoced", PayrollRun.thirteenth(year=2026, payment_month=12)),
    ],
)
def test_unknown_days_do_not_block_ineligible_runs(
    headcount: int, ccnl_id: str, run: PayrollRun | None
) -> None:
    """Outside daily entitlement, zero hypothetical EUR 8 vouchers need no day fact."""
    result = _run(
        year=2026, month=12, days=None, headcount=headcount, ccnl_id=ccnl_id, run=run
    )
    assert not [i for i in result.issues if i.fact == "meal_benefit_days"]


@pytest.mark.parametrize(
    ("started_on", "ended_on", "days", "valid_days"),
    [
        (date(2026, 10, 21), None, 12, 11),
        (date(2026, 10, 1), date(2026, 10, 10), 11, 10),
    ],
)
def test_days_cannot_exceed_employed_span(
    started_on: date, ended_on: date | None, days: int, valid_days: int
) -> None:
    """October hire/termination: 11/10 employed days pay EUR 88/80, not EUR 96/88."""
    run = (
        PayrollRun(run_kind=RunKind.TERMINATION, year=2026, month=10)
        if ended_on is not None
        else None
    )
    with pytest.raises(InvalidInputError, match="exceeds employed days"):
        _run(
            year=2026,
            month=10,
            days=days,
            started_on=started_on,
            ended_on=ended_on,
            run=run,
        )
    result = _run(
        year=2026,
        month=10,
        days=valid_days,
        started_on=started_on,
        ended_on=ended_on,
        run=run,
    )
    assert (
        sum(
            (i.amount for i in result.pay_items if i.kind == "welfare_item"), Decimal(0)
        )
        == Decimal(8) * valid_days
    )


def test_unknown_days_on_termination_run() -> None:
    """A terminated worker with unknown days posts EUR 0 and needs the fact."""
    result = _run(
        year=2026,
        month=10,
        days=None,
        ended_on=date(2026, 10, 10),
        run=PayrollRun(run_kind=RunKind.TERMINATION, year=2026, month=10),
    )
    assert not [i for i in result.pay_items if i.kind == "welfare_item"]
    assert any(i.fact == "meal_benefit_days" for i in result.issues)


def test_days_must_fit_competence_month() -> None:
    """February 2026 cannot include 30 eligible EUR 8 voucher days."""
    with pytest.raises(InvalidInputError, match="meal_benefit_days"):
        _run(year=2026, month=2, days=30)


def test_extra_month_has_no_eligible_voucher_days() -> None:
    """An extra-month run cannot claim EUR 8 * 1 = EUR 8 of vouchers."""
    with pytest.raises(InvalidInputError, match="regular or termination"):
        _run(
            year=2026,
            month=12,
            days=1,
            run=PayrollRun.thirteenth(year=2026, payment_month=12),
        )


def test_no_contract_rate_does_not_guess_a_voucher_value() -> None:
    """A contract without a daily rate cannot guess EUR 8 for one day."""
    with pytest.raises(InvalidInputError, match="no contractual daily"):
        _run(year=2026, month=1, days=1, ccnl_id="commercio-confcommercio")


def test_headcount_is_a_strict_threshold() -> None:
    """Ten employees cannot qualify for EUR 8 * 1 = EUR 8 of meal benefits."""
    with pytest.raises(InvalidInputError, match="more than 10"):
        _run(year=2026, month=10, days=1, headcount=10)


@pytest.mark.parametrize("days", [-1, 32, True, 2.5])
def test_invalid_eligible_days_are_rejected(days: object) -> None:
    """Only integral eligible counts from 0 through 31 can generate benefits."""
    with pytest.raises(InvalidInputError):
        PeriodFacts(meal_benefit_days=days)  # type: ignore[arg-type]
