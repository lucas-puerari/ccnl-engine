"""Seniority increments: state the recognised seniority as a dated fact."""

from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import SeniorityFact, SenioritySource, WorkerCategory

engine = PayrollEngine.bundled()
run = PayrollRun.regular(year=2026, month=1)
payment = date(2026, 1, 28)
employer = EmployerProfile(headcount=Headcount(100))


def seniority_reason(seniority: SeniorityFact | None) -> None:
    """Print the gross, the seniority decision and the payability of a run."""
    result = engine.calculate_period(
        PeriodInput(
            run=run,
            payment_date=payment,
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                seniority=seniority,
            ),
            employer=employer,
        )
    )
    (decision,) = (d for d in result.decisions if d.capability == "seniority")
    print(
        f"{result.period_gross}  {decision.reason_code:22s} "
        f"amount={decision.amount}  payable={result.is_payable}"
    )


# Unknown: the increments are undetermined, a missing_fact blocker names it.
seniority_reason(None)
# A new hire: zero increments, confirmed.
seniority_reason(SeniorityFact.since(date(2026, 1, 1), SenioritySource.PAYSLIP))
# 60 months on 1 January 2026: the engine ages the fact to each run.
seniority_reason(SeniorityFact(60, date(2026, 1, 1), SenioritySource.PAYSLIP))

# Category-specific increments: FISE level 2 at 60 months of service pays
# 56.66 to an operaio and 62.62 to an impiegato.
for category in (WorkerCategory.OPERAIO, WorkerCategory.IMPIEGATO):
    result = engine.calculate_period(
        PeriodInput(
            run=run,
            payment_date=payment,
            employment=Employment(
                ccnl_slug="servizi-postali-appalto-fise.json",
                level_code="2",
                seniority=SeniorityFact(
                    60, date(2026, 1, 1), SenioritySource.EMPLOYER_RECORDS
                ),
                category=category,
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
        )
    )
    print(f"FISE L2 {category}: {result.period_gross}")
