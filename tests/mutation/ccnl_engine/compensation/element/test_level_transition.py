"""The time-limited junior level and its mandatory promotion."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

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
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.services import _resolve_chain
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.entry.transition import transitioned_level
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.fact.services import level_start_issue
from ccnl_engine.employment.inputs import Apprentice, Permanent
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.period.context.services import RunContext
from ccnl_engine.seniority.inputs import (
    EarnedIncrements,
    SeniorityFact,
    SenioritySource,
)


def _chain(month: date, started_on: date | None) -> MonthlyPayChain:
    ccnl = load_ccnl("logistica-trasporto-confetra")
    chain, _ = _resolve_chain(
        ccnl,
        ccnl.level_by_code("6J"),
        Permanent(),
        month,
        seniority_months=None,
        roles=frozenset(),
        worker_category=None,
        hired_on=date(2025, 6, 1),
        level_started_on=started_on,
    )
    return chain


def test_junior_pay_and_cutoff() -> None:
    """2025: 1464.53 + 7.58 = 1472.11; 2026: 1648.74 + 8.26 = 1657.00."""
    junior = _chain(date(2025, 11, 1), date(2025, 6, 1))
    assert junior.base == Decimal("1464.53")
    assert sum((value for _, value in junior.allowances), Decimal()) == Decimal("7.58")
    promoted = _chain(date(2026, 1, 1), date(2025, 6, 1))
    assert promoted.base == Decimal("1648.74")
    assert sum((value for _, value in promoted.allowances), Decimal()) == Decimal(
        "8.26"
    )


def test_twelve_month_promotion_and_missing_start() -> None:
    """A 2024 level start pays 1615.71; unknown start blocks 1464.53."""
    assert _chain(date(2025, 6, 1), date(2024, 1, 1)).base == Decimal("1615.71")
    assert _chain(date(2025, 6, 1), None).base == Decimal("1464.53")
    ccnl = load_ccnl("logistica-trasporto-confetra")

    def context(month: date, level: str) -> RunContext:
        return cast(
            "RunContext",
            SimpleNamespace(
                contract=SimpleNamespace(
                    level=ccnl.level_by_code(level),
                    tctx=SimpleNamespace(competence=month),
                ),
                request=SimpleNamespace(level_started_on=None),
            ),
        )

    issue = level_start_issue(context(date(2025, 6, 1), "6J"))
    assert issue is not None
    assert issue.fact == "level_started_on"
    assert level_start_issue(context(date(2026, 1, 1), "6J")) is None
    assert level_start_issue(context(date(2025, 6, 1), "6")) is None


def test_period_uses_promoted_level_without_entry_date() -> None:
    """January 2026 gross: level 6 minimum 1648.74 + EDR 8.26 = 1657.00."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 25),
            employment=Employment(
                ccnl_id="logistica-trasporto-confetra",
                level_code="6J",
                contract_type=Permanent(),
                category=WorkerCategory.OPERAIO,
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="F205"),
        )
    )
    assert result.period_gross == Decimal("1657.00")
    assert all(issue.code != "entry_level_start_unknown" for issue in result.issues)


def test_unsupported_apprentice_and_cutoff() -> None:
    """The 2025 apprentice cannot receive 1464.53 without the 24-month rule."""
    ccnl = load_ccnl("logistica-trasporto-confetra")
    junior = ccnl.level_by_code("6J")
    apprentice = Apprentice(months_elapsed=6)
    with pytest.raises(InvalidInputError, match="apprenticeship"):
        transitioned_level(ccnl, junior, apprentice, date(2025, 11, 1), None)
    assert (
        transitioned_level(ccnl, junior, apprentice, date(2026, 1, 1), None).code == "6"
    )


def test_hire_cohorts_and_unsupported_history() -> None:
    """At 18 months a 2019 hire gets 1615.71; at 18 a 2018 hire gets 1464.53."""
    ccnl = load_ccnl("logistica-trasporto-confetra")
    junior = ccnl.level_by_code("6J")
    start = date(2024, 1, 1)
    for hire, month, expected in (
        (date(2018, 1, 1), date(2025, 7, 1), "6J"),
        (date(2019, 1, 1), date(2025, 7, 1), "6"),
        (date(2020, 1, 1), date(2025, 1, 1), "6"),
    ):
        assert (
            transitioned_level(
                ccnl, junior, Permanent(), month, start, hired_on=hire
            ).code
            == expected
        )
    with pytest.raises(InvalidInputError, match="2017 level history"):
        transitioned_level(
            ccnl,
            junior,
            Permanent(),
            date(2025, 7, 1),
            start,
            hired_on=date(2017, 12, 31),
        )
    with pytest.raises(InvalidInputError, match="hire date"):
        transitioned_level(ccnl, junior, Permanent(), date(2025, 7, 1), start)
    target_periods = ccnl.level_by_code("6").base_salary.periods
    for fallback, target in zip(
        junior.base_salary.periods[1:], target_periods[1:], strict=True
    ):
        assert fallback.value == target.value
        assert fallback.provenance is not None
        assert fallback.provenance.transformation is not None
        assert "NEVER PAID" in fallback.provenance.transformation


def test_period_selects_hire_cohort_from_employment_period() -> None:
    """At 18 months: 2019 hire gets 1615.71 + 8.26 = 1623.97, not 1472.11."""

    def gross(hire: date) -> Decimal:
        request = PeriodInput(
            run=PayrollRun.regular(year=2025, month=7),
            payment_date=date(2025, 7, 25),
            employment=Employment(
                ccnl_id="logistica-trasporto-confetra",
                level_code="6J",
                contract_type=Permanent(),
                category=WorkerCategory.OPERAIO,
                employment_period=EmploymentPeriod(started_on=hire),
                level_started_on=date(2024, 1, 1),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="F205"),
        ).calculation_request()
        ccnl = load_ccnl(request.ccnl_id)
        assert request.employment_period is not None
        chain, _ = _resolve_chain(
            ccnl,
            ccnl.level_by_code(request.level_code),
            request.contract_type,
            date(2025, 7, 1),
            seniority_months=None,
            hired_on=request.employment_period.started_on,
            level_started_on=request.level_started_on,
        )
        return chain.base + sum((amount for _, amount in chain.allowances), Decimal())

    assert gross(date(2019, 1, 1)) == Decimal("1623.97")
    assert gross(date(2018, 1, 1)) == Decimal("1472.11")


def test_matured_junior_steps_refused_on_promotion() -> None:
    """Preserve 18.78, not level-6 20.66: 1615.71 + 8.26 + 18.78 = 1642.75."""
    ccnl = load_ccnl("logistica-trasporto-confetra")
    with pytest.raises(InvalidInputError, match="prior-level increments"):
        _resolve_chain(
            ccnl,
            ccnl.level_by_code("6J"),
            Permanent(),
            date(2025, 6, 1),
            seniority_months=24,
            hired_on=date(2020, 1, 1),
            level_started_on=date(2024, 1, 1),
        )
    with pytest.raises(InvalidInputError, match="prior-level increments"):
        _resolve_chain(
            ccnl,
            ccnl.level_by_code("6J"),
            Permanent(),
            date(2026, 1, 1),
            seniority_months=48,
            hired_on=date(2020, 1, 1),
            level_started_on=date(2025, 1, 1),
        )


def test_period_refuses_matured_steps_after_cutoff() -> None:
    """Retain a matured 18.78 step, not 20.66: refusing avoids 1.88 excess."""
    with pytest.raises(InvalidInputError, match="prior-level increments"):
        PayrollEngine.bundled().calculate_period(
            PeriodInput(
                run=PayrollRun.regular(year=2026, month=1),
                payment_date=date(2026, 1, 25),
                employment=Employment(
                    ccnl_id="logistica-trasporto-confetra",
                    level_code="6J",
                    contract_type=Permanent(),
                    category=WorkerCategory.OPERAIO,
                    employment_period=EmploymentPeriod(started_on=date(2020, 1, 1)),
                    level_started_on=date(2025, 1, 1),
                    seniority=SeniorityFact.since(
                        date(2023, 1, 1), SenioritySource.EMPLOYER_RECORDS
                    ),
                ),
                employer=EmployerProfile(headcount=Headcount(50)),
                facts=PeriodFacts(regione="IT-25", comune_belfiore="F205"),
            )
        )


def test_stated_earned_junior_step_survives_cutoff() -> None:
    """January 2026: 1648.74 + 8.26 + retained 18.78 = 1675.78, not 1677.66."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 25),
            employment=Employment(
                ccnl_id="logistica-trasporto-confetra",
                level_code="6J",
                contract_type=Permanent(),
                category=WorkerCategory.OPERAIO,
                seniority=SeniorityFact(
                    36,
                    date(2026, 1, 1),
                    SenioritySource.PAYSLIP,
                    earned=EarnedIncrements(1, Decimal("18.78")),
                ),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="F205"),
        )
    )
    assert result.period_gross == Decimal("1675.78")


def test_earned_step_keeps_unfinished_biennium() -> None:
    """One retained 18.78 plus the next level-6 step 20.66 = 39.44."""
    ccnl = load_ccnl("logistica-trasporto-confetra")
    seniority = SeniorityFact(
        47,
        date(2026, 1, 1),
        SenioritySource.PAYSLIP,
        earned=EarnedIncrements(1, Decimal("18.78")),
    )
    chain, _ = _resolve_chain(
        ccnl,
        ccnl.level_by_code("6J"),
        Permanent(),
        date(2026, 2, 1),
        seniority_months=48,
        seniority=seniority,
    )
    assert chain.seniority == Decimal("39.44")


def test_level_start_date_validation() -> None:
    """A 2025-06 entry cannot precede a 2025-07 hire or follow June 2025 pay."""
    with pytest.raises(InvalidInputError, match=r"Employment\.level_started_on"):
        Employment(
            ccnl_id="logistica-trasporto-confetra",
            level_code="6J",
            contract_type=Permanent(),
            employment_period=EmploymentPeriod(started_on=date(2025, 7, 1)),
            level_started_on=date(2025, 6, 1),
        )
    with pytest.raises(InvalidInputError, match=r"Employment\.level_started_on"):
        PeriodInput(
            run=PayrollRun.regular(year=2025, month=6),
            payment_date=date(2025, 6, 25),
            employment=Employment(
                ccnl_id="logistica-trasporto-confetra",
                level_code="6J",
                contract_type=Permanent(),
                level_started_on=date(2025, 7, 1),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="F205"),
        ).calculation_request()


def test_transition_without_months_and_invalid_targets() -> None:
    """The cutoff is independent of tenure; invalid transition targets fail loading."""
    ccnl = load_ccnl("logistica-trasporto-confetra")
    junior = ccnl.level_by_code("6J")
    by_cutoff = junior.model_copy(
        update={"transition_after_months": None, "transition_hire_bands": ()}
    )
    assert (
        transitioned_level(ccnl, by_cutoff, Permanent(), date(2025, 11, 1), None).code
        == "6J"
    )
    for changes, message in (
        ({"transition_to": None}, "without a target"),
        ({"transition_to": "unknown"}, "invalid transition target"),
        ({"transition_to": "6J"}, "invalid transition target"),
    ):
        invalid_level = junior.model_copy(update=changes)
        invalid = ccnl.model_copy(update={"levels": (invalid_level, *ccnl.levels[1:])})
        with pytest.raises(ValueError, match=message):
            invalid._assert_level_transitions()
