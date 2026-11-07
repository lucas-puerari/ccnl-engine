"""The ratei maturati and the TFR accrued a payslip prints as progressivi.

Turismo Federalberghi level 4 pays a tredicesima in December (window January
to December) and a quattordicesima in July (window July to June); the
months count by the CCNL month rule.  Federmeccanica pays a tredicesima
only.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import ExtraMonthProgress
from ccnl_engine.run.types import RunKind

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(20))
_THIRTEENTH, _FOURTEENTH = "thirteenth", "fourteenth"


def _employment(
    ccnl: str = "turismo-federalberghi",
    level: str = "4",
    period: EmploymentPeriod | None = None,
) -> Employment:
    hired = date(2025, 1, 1)
    return Employment(
        ccnl_id=ccnl,
        level_code=level,
        contract_type=Permanent(),
        employment_period=period or EmploymentPeriod(hired, None),
        seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
        pension_fund=NoPensionFund(),
        tfr_treasury_fund=False,
    )


def _run(month: int, employment: Employment | None = None) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=employment or _employment(),
            employer=_EMPLOYER,
        )
    )


def _ratei(result: PeriodResult) -> dict[str, tuple[int, Decimal]]:
    return {
        e.kind.value: (e.payment_year, e.months)
        for e in result.progressives.extra_months
    }


def test_march_counts_each_window_to_its_month() -> None:
    """March: 3 ratei of the 2026 tredicesima, 9 of the July 2026 one."""
    progress = _run(3).progressives.extra_months

    assert _ratei(_run(3)) == {
        _THIRTEENTH: (2026, Decimal(3)),
        _FOURTEENTH: (2026, Decimal(9)),
    }
    assert [p.fraction for p in progress] == [Decimal(3) / 12, Decimal(9) / 12]


def test_august_starts_the_next_quattordicesima() -> None:
    """August: the window of July 2027 holds July and August."""
    assert _ratei(_run(8))[_FOURTEENTH] == (2027, Decimal(2))


def test_a_hire_in_the_year_counts_from_its_month() -> None:
    """Hired on 1 February 2026: 2 ratei of the tredicesima in March."""
    employment = _employment(period=EmploymentPeriod(date(2026, 2, 1), None))

    assert _ratei(_run(3, employment))[_THIRTEENTH] == (2026, Decimal(2))


def test_a_termination_counts_to_its_last_day() -> None:
    """Out on 31 March: the ratei stop there, as the settlement pays them."""
    employment = _employment(
        period=EmploymentPeriod(date(2025, 1, 1), date(2026, 3, 31))
    )

    assert _ratei(_run(3, employment))[_THIRTEENTH] == (2026, Decimal(3))


def test_the_plan_accrues_the_tfr_run_by_run() -> None:
    """Federmeccanica 2026: the TFR accrued grows with each run of the year.

    The extra-month run has no ratei of its own to print.
    """
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment("metalmeccanico-federmeccanica", "C3"),
            employer=_EMPLOYER,
        )
    )
    runs = {(r.run.run_kind, r.run.month): r for r in year.period_results if r.run}
    accrued = [runs[RunKind.REGULAR, m].progressives.tfr_accrued for m in range(1, 13)]

    assert runs[RunKind.THIRTEENTH, 12].progressives.extra_months == ()
    known = [a for a in accrued if a is not None]
    assert len(known) == 12
    assert all(a > 0 for a in known)
    assert known == sorted(known)
    assert runs[RunKind.REGULAR, 12].progressives.extra_months == (
        ExtraMonthProgress(
            kind=runs[RunKind.REGULAR, 12].progressives.extra_months[0].kind,
            payment_year=2026,
            months=Decimal(12),
            fraction=Decimal(1),
        ),
    )
