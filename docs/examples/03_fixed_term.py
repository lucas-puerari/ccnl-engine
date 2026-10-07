"""Fixed-term employment renewed once: the NASpI surcharge is 1.4% + 0.5%."""

from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import FixedTerm, NaspiExclusion

engine = PayrollEngine.bundled()

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            # Second fixed-term contract with the employer, no exclusion of
            # L. 92/2012 art. 2 c. 29: surcharge 1.4% + 0.5% (c. 28).
            contract_type=FixedTerm(renewals=1, naspi_exclusion=NaspiExclusion.NONE),
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    )
)

print(f"Period gross: {result.period_gross}")
print(f"Period net:   {result.period_net}")
print(f"Employer cost (includes the NASpI surcharge): {result.period_employer_cost}")
(employer,) = (d for d in result.decisions if d.capability == "inps_employer")
print(f"NASpI surcharge rate: {employer.inputs['naspi_surcharge_rate']}")
