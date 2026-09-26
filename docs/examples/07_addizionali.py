"""Regional and municipal surtax: declare regione and comune_belfiore."""

from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)

engine = PayrollEngine.bundled()


def january(facts: PeriodFacts) -> PeriodInput:
    """Build a Metalmeccanico C3 run for January 2026.

    Returns:
        The period input with ``facts``.
    """
    return PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
        ),
        employer=EmployerProfile(headcount=Headcount(100)),
        facts=facts,
    )


# No surtax (default)
result_no_surtax = engine.calculate_period(january(PeriodFacts()))

# Emilia-Romagna region + Modena municipality
result_surtax = engine.calculate_period(
    january(PeriodFacts(regione="IT-45", comune_belfiore="F257"))  # Modena
)

print(f"Net (no surtax):   {result_no_surtax.period_net}")
print(f"Net (IT-45 Modena): {result_surtax.period_net}")
print(f"Surtax withheld:   {result_no_surtax.period_net - result_surtax.period_net}")
print(f"Status:            {result_surtax.status}")  # final: both tables known
for decision in result_surtax.decisions:
    print(f"  {decision.capability}: {decision.reason_code} {decision.amount}")
