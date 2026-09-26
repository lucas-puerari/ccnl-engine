"""Apprenticeship: reduced salary percentage from CCNL percentage track."""

from datetime import date

from ccnl_engine import (
    Apprentice,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)

engine = PayrollEngine.bundled()


def apprentice_period(months_elapsed: int) -> PeriodInput:
    """Build a Commercio level 4 apprentice run for January 2026.

    Returns:
        The period input at ``months_elapsed`` months of apprenticeship.
    """
    return PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            contract_type=Apprentice(months_elapsed=months_elapsed),
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    )


# Month 0: start of apprenticeship (lowest percentage)
result_start = engine.calculate_period(apprentice_period(0))

# Month 24: further into the track (higher percentage)
result_24 = engine.calculate_period(apprentice_period(24))

print(f"Gross at month 0:   {result_start.period_gross}")
print(f"Gross at month 24:  {result_24.period_gross}")
