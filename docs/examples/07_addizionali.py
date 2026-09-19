"""Regional and municipal IRPEF surcharges (addizionali).

By default the engine omits addizionale regionale and comunale
(they appear in fiscal_simplifications). Set jurisdiction on Employee
with regione / comune_belfiore to include them.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    FiscalSimplification,
    Jurisdiction,
    AnnualPayrollScenario,
    Permanent,
    estimate_annual,
)

# Baseline: no jurisdiction → addizionali are zero.
baseline = estimate_annual(
    AnnualPayrollScenario(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
).result

# Worker resident in Romano di Lombardia (codice catastale H509), Lombardia.
# Addizionale comunale: 0.80% with soglia 12 000 EUR.
p = estimate_annual(
    AnnualPayrollScenario(
        employee=Employee(
            level_code="4",
            jurisdiction=Jurisdiction(
                regione="Lombardia",
                comune_belfiore="H509",  # Romano di Lombardia
            ),
        ),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
).result

print(f"Net annual (no addizionali):    {baseline.net_annual} EUR")
print(f"Net annual (with addizionali):  {p.net_annual} EUR")
print(f"Addizionale regionale:          {p.taxes.addizionale_regionale_annual} EUR")
print(f"Addizionale comunale:           {p.taxes.addizionale_comunale_annual} EUR")

# When addizionali are computed they are no longer in fiscal_simplifications.
assert (
    FiscalSimplification.NO_ADDIZIONALE_REGIONALE not in p.taxes.fiscal_simplifications
)
assert (
    FiscalSimplification.NO_ADDIZIONALE_COMUNALE not in p.taxes.fiscal_simplifications
)
assert p.taxes.addizionale_regionale_annual > Decimal(0)
assert p.taxes.addizionale_comunale_annual > Decimal(0)
