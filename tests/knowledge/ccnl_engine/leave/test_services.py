"""Hand oracles of the leave accrual, the leave taken and the residual paid.

Each oracle is computed by hand in the test, in ``Decimal``, from the CCNL
values stated in its docstring, independently of the engine internals.

Commercio (Testo Unico 30 luglio 2019): 26 working days of ferie a year
(Art. 159, p. 157), accrued in twelfths per month of service (Art. 162,
p. 159); 32 hours of ex festività (Art. 158 c. 1, p. 155: the 4 abolished
festivities in groups of 8 hours) and 72 hours of ROL in a company with
more than 15 employees (Art. 158 cc. 3-4, pp. 155-156), both by whole
months of service (p. 156); the ROL of a worker hired after 1 March 2011
accrues 0% for the first two years, 50% up to four, 100% after (p. 156).
The indemnity for the ferie left at the end of the employment is the
monthly retribuzione di fatto over 26 (Art. 159, chiarimento a verbale,
p. 157); the hours of permits left are paid at the monthly pay over the
hourly divisor 168 (Art. 211 lett. a, p. 197).

The task asked for 16 hours of ROL; under Art. 158 a worker hired on 1
January 2026 accrues no ROL before January 2028, so the oracle takes the
16 hours from the ex festività, the only permit bucket that accrues for
him.  Taking them from the ROL instead overdraws it, and the engine then
pays no residual (:func:`test_commercio_rol_taken_beyond_accrual_pays_nothing`).

Turismo (CCNL 20 febbraio 2010): 26 days of ferie (Art. 129 c. 1, p. 124)
and a single pool of 104 hours of reduction holding the 32 hours of ex
festività (Art. 111 cc. 1-3, p. 114).  No clause read gives the basis of
the indemnity at termination: the residual stays unpaid and the run is
not payable.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Final

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import AbsenceEvent, LeaveBucket, LeaveTakenEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
    WorkerCategory,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine import CompetenceYearResult, PeriodResult
    from ccnl_engine.inputs import LeaveBalance

_HIRED: Final = date(2026, 1, 1)
_ENDED: Final = date(2026, 10, 31)
_TWELVE: Final = Decimal(12)
_CENT: Final = Decimal("0.01")
_FACTS: Final = PeriodFacts(
    regione="IT-25", comune_belfiore="A005", family_composition=FamilyComposition()
)


@pytest.fixture(scope="module")
def engine() -> PayrollEngine:
    """Return the bundled engine.

    Returns:
        The engine in simulation mode.
    """
    return PayrollEngine.bundled()


_EMPLOYER: Final = EmployerProfile(
    headcount=Headcount(20), provincial_pay_element=False
)


def _employment(ccnl_id: str, level: str, ended_on: date | None) -> Employment:
    return Employment(
        ccnl_id=ccnl_id,
        level_code=level,
        contract_type=Permanent(),
        category=WorkerCategory.IMPIEGATO,
        employment_period=EmploymentPeriod(_HIRED, ended_on),
        seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
        roles=frozenset(),
        sector=EmploymentSector.PRIVATE,
        pension_fund=NoPensionFund(),
        tfr_treasury_fund=True,
    )


def _year(
    engine: PayrollEngine,
    ccnl_id: str,
    level: str,
    events: Mapping[int, tuple[LeaveTakenEvent, ...]],
    ended_on: date | None = _ENDED,
) -> CompetenceYearResult:
    return engine.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment(ccnl_id, level, ended_on),
            employer=_EMPLOYER,
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40000)),
            default_facts=_FACTS,
            periods={
                month: replace(_FACTS, events=taken) for month, taken in events.items()
            },
        )
    )


def _run(year: CompetenceYearResult, run_id: str) -> PeriodResult:
    return next(r for r in year.period_results if str(r.run.run_id) == run_id)  # type: ignore[union-attr]


def _balance(result: PeriodResult, bucket: LeaveBucket) -> LeaveBalance:
    return next(b for b in result.leave_balances if b.bucket is bucket)


def _settled(result: PeriodResult) -> dict[str, Decimal]:
    return {
        item.item_id.split("_2026")[0]: item.amount
        for item in result.pay_items
        if item.kind == "leave_settlement_item"
    }


def _decision(result: PeriodResult, capability: str) -> tuple[str, str]:
    found = {
        (d.status.value, d.reason_code)
        for d in result.decisions
        if d.capability == capability
    }
    (decision,) = found
    return decision


_COMMERCIO_TAKEN: Final = {
    7: (
        LeaveTakenEvent(date(2026, 7, 6), LeaveBucket.FERIE, Decimal(10)),
        LeaveTakenEvent(date(2026, 7, 20), LeaveBucket.EX_FESTIVITA, Decimal(16)),
    )
}


def test_commercio_oracle_accrual_balance_and_payout(engine: PayrollEngine) -> None:
    """Commercio level 4, hired 1 January 2026, 20 employees, ended 31 October 2026.

    Monthly retribuzione di fatto in October 2026 (tranche of 1 November
    2025): paga base 1,257.46 + contingenza and EDR 524.22 + terzo elemento
    nazionale 2.07 (no provincial element) = 1,783.75.  Ten whole months
    of service; in July the worker takes 10 days of ferie and 16 hours of
    ex festività.

    - ferie: 26 x 10 / 12 = 21.6667 days accrued, 11.6667 left;
      11.6667 x 1,783.75 / 26 = 800.40;
    - ex festività: 32 x 10 / 12 = 26.6667 hours accrued, 10.6667 left;
      10.6667 x 1,783.75 / 168 = 113.25;
    - ROL: 72 hours a year at 0% in the first two years: nothing.
    """
    year = _year(engine, "commercio-confcommercio", "4", _COMMERCIO_TAKEN)
    monthly = Decimal("1257.46") + Decimal("524.22") + Decimal("2.07")
    months = Decimal(10)
    ferie_left = Decimal(26) * months / _TWELVE - Decimal(10)
    ex_fest_left = Decimal(32) * months / _TWELVE - Decimal(16)
    ferie_pay = (ferie_left * monthly / Decimal(26)).quantize(_CENT)
    ex_fest_pay = (ex_fest_left * monthly / Decimal(168)).quantize(_CENT)

    october = _run(year, "2026-10-regular")

    assert monthly == Decimal("1783.75")
    assert (ferie_pay, ex_fest_pay) == (Decimal("800.40"), Decimal("113.25"))
    assert _settled(october) == {
        "leave_ferie": ferie_pay,
        "leave_ex_festivita": ex_fest_pay,
    }
    assert _decision(october, "termination_residual_leave") == (
        "final",
        "residual_leave_paid",
    )
    ferie = _balance(october, LeaveBucket.FERIE)
    ex_fest = _balance(october, LeaveBucket.EX_FESTIVITA)
    rol = _balance(october, LeaveBucket.ROL)
    assert (ferie.accrued, ferie.taken, ferie.paid, ferie.residual) == (
        Decimal(26) * months / _TWELVE,
        Decimal(10),
        ferie_left,
        Decimal(0),
    )
    assert (ex_fest.accrued, ex_fest.taken, ex_fest.paid) == (
        Decimal(32) * months / _TWELVE,
        Decimal(16),
        ex_fest_left,
    )
    assert (rol.accrued, rol.taken, rol.residual) == (Decimal(0),) * 3
    assert october.capability_report.gaps == ()


def test_commercio_balance_before_the_termination(engine: PayrollEngine) -> None:
    """After September: 26 x 9 / 12 - 10 days and 32 x 9 / 12 - 16 hours left."""
    year = _year(engine, "commercio-confcommercio", "4", _COMMERCIO_TAKEN)
    september = _run(year, "2026-09-regular")
    july = _run(year, "2026-07-regular")

    ferie_left = Decimal(26) * 9 / _TWELVE - 10
    ex_fest_left = Decimal(32) * 9 / _TWELVE - 16

    assert _balance(september, LeaveBucket.FERIE).residual == ferie_left
    assert _balance(september, LeaveBucket.EX_FESTIVITA).residual == ex_fest_left
    assert _settled(september) == {}
    assert _decision(july, "leave") == ("final", "paid_in_monthly_pay")
    assert july.period_gross == Decimal("1783.75")


def test_commercio_rol_taken_beyond_accrual_pays_nothing(
    engine: PayrollEngine,
) -> None:
    """16 hours of ROL for a 2026 hire overdraw it: no residual is paid."""
    taken = {
        7: (LeaveTakenEvent(date(2026, 7, 20), LeaveBucket.ROL, Decimal(16)),),
    }
    year = _year(engine, "commercio-confcommercio", "4", taken)
    october = _run(year, "2026-10-regular")

    assert _balance(october, LeaveBucket.ROL).residual == Decimal(-16)
    assert _settled(october) == {}
    assert _decision(october, "termination_residual_leave") == (
        "incomplete",
        "leave_taken_beyond_accrual",
    )
    assert not october.is_payable


def test_commercio_balances_carry_into_the_next_year(engine: PayrollEngine) -> None:
    """The 2026 residual is carried into 2027 and taken first.

    2026: 26 days and 32 hours of ex festività accrued over twelve months,
    nothing taken.  January 2027: 30 days of ferie taken, 26 from the 2026
    balance and 4 from the 2027 one, which accrued 26 / 12 in January.
    """
    first = _year(engine, "commercio-confcommercio", "4", {}, ended_on=None)
    january = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2027, 1),
            payment_date=date(2027, 1, 27),
            employment=_employment("commercio-confcommercio", "4", None),
            employer=_EMPLOYER,
            facts=replace(
                _FACTS,
                events=(
                    LeaveTakenEvent(date(2027, 1, 4), LeaveBucket.FERIE, Decimal(30)),
                ),
            ),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40000)),
            opening_state=PayrollEngine.close_tax_year(first.closing_state),
        )
    )

    ferie = [b for b in january.leave_balances if b.bucket is LeaveBucket.FERIE]
    assert [(b.year, b.accrued, b.taken, b.residual) for b in ferie] == [
        (2026, Decimal(26), Decimal(26), Decimal(0)),
        (2027, Decimal(26) / _TWELVE, Decimal(4), Decimal(26) / _TWELVE - 4),
    ]


_TURISMO_TAKEN: Final = {
    4: (LeaveTakenEvent(date(2026, 4, 13), LeaveBucket.FERIE, Decimal(6)),),
    5: (LeaveTakenEvent(date(2026, 5, 18), LeaveBucket.ROL, Decimal(24)),),
}


def test_turismo_oracle_accrual_and_balance(engine: PayrollEngine) -> None:
    """Turismo level 4, hired 1 January 2026, ended 31 October 2026.

    6 days of ferie taken in April and 24 hours of the 104-hour pool in May.

    - after June: ferie 26 x 6 / 12 = 13 accrued, 7 left; pool 104 x 6 / 12
      = 52 hours accrued, 28 left;
    - after October: ferie 26 x 10 / 12 - 6 = 15.6667 days left, pool
      104 x 10 / 12 - 24 = 62.6667 hours left, not paid: the indemnity has
      no sourced basis, so the run is not payable.
    """
    year = _year(engine, "turismo-federalberghi", "4", _TURISMO_TAKEN)
    june = _run(year, "2026-06-regular")
    october = _run(year, "2026-10-regular")

    assert [
        (b.bucket, b.accrued, b.taken, b.residual) for b in june.leave_balances
    ] == [
        (LeaveBucket.FERIE, Decimal(13), Decimal(6), Decimal(7)),
        (LeaveBucket.ROL, Decimal(52), Decimal(24), Decimal(28)),
    ]
    assert [b.residual for b in october.leave_balances] == [
        Decimal(26) * 10 / _TWELVE - 6,
        Decimal(104) * 10 / _TWELVE - 24,
    ]
    assert _settled(october) == {}
    assert _decision(october, "termination_residual_leave") == (
        "incomplete",
        "termination_basis_not_sourced",
    )
    assert not october.is_payable


def test_turismo_ex_festivita_is_inside_the_pool(engine: PayrollEngine) -> None:
    """Hours taken as ex festività are not a bucket of Turismo: not decided."""
    taken = {
        5: (LeaveTakenEvent(date(2026, 5, 18), LeaveBucket.EX_FESTIVITA, Decimal(8)),),
    }
    year = _year(engine, "turismo-federalberghi", "4", taken, ended_on=None)
    may = _run(year, "2026-05-regular")

    assert _decision(may, "leave") == ("incomplete", "leave_bucket_not_modelled")


def test_part_time_and_suspended_days_in_the_accrual(engine: PayrollEngine) -> None:
    """Commercio at 20 of 40 hours, two days of aspettativa in February.

    January: ex festività 32 x 0.5 / 12 = 1.3333 hours, ferie 26 / 12 days.
    February is not served whole: the ex festività (whole months only)
    accrue nothing, the ferie (month rule not stated) nothing, inexactly.
    """
    absence = AbsenceEvent(
        event_date=date(2026, 2, 2),
        end_date=date(2026, 2, 3),
        hours=Decimal(8),
        hourly_rate=Decimal(10),
        suspends_accrual=True,
        no_pay_due=True,
    )
    year = engine.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=replace(
                _employment("commercio-confcommercio", "4", date(2026, 2, 28)),
                weekly_hours=WeeklyHours(Decimal(20)),
                full_time_weekly_hours=WeeklyHours(Decimal(40)),
            ),
            employer=_EMPLOYER,
            prior_year=PriorYearTaxFacts(employment_income=Decimal(40000)),
            default_facts=_FACTS,
            periods={2: replace(_FACTS, events=(absence,))},
        )
    )
    february = _run(year, "2026-02-regular")

    assert [(b.bucket, b.accrued, b.exact) for b in february.leave_balances] == [
        (LeaveBucket.FERIE, Decimal(26) / _TWELVE, False),
        (LeaveBucket.ROL, Decimal(0), True),
        (LeaveBucket.EX_FESTIVITA, Decimal(16) / _TWELVE, True),
    ]
    assert _decision(february, "termination_residual_leave") == (
        "provisional",
        "residual_leave_estimated",
    )
