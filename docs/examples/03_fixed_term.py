"""Fixed-term contract: NASpI addizionale on employer INPS.

FixedTerm() adds the 1.40% NASpI addizionale to the employer's INPS
contribution (Art. 2 c. 28 L. 92/2012). Everything else is identical
to a permanent contract.
"""

from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    FixedTerm,
    PayrollScenario,
    Permanent,
    compute,
)

permanent = compute(
    PayrollScenario(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 1, 1),
        ),
    )
)
fixed_term = compute(
    PayrollScenario(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=FixedTerm(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 1, 1),
        ),
    )
)

print(f"Employer INPS — permanent:   {permanent.inps_employer_annual} EUR")
print(f"Employer INPS — fixed-term:  {fixed_term.inps_employer_annual} EUR")
print(
    f"NASpI addizionale:           "
    f"{fixed_term.inps_employer_annual - permanent.inps_employer_annual} EUR"
)

# Gross and net are identical; only the employer side differs.
assert fixed_term.net_annual == permanent.net_annual
assert fixed_term.inps_employer_annual > permanent.inps_employer_annual
