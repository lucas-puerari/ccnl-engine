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
    PayrollScenario,
    Permanent,
    compute,
)

# Baseline: no jurisdiction → addizionali are zero.
baseline = compute(
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

# Worker resident in Romano di Lombardia (codice belfiore H509), Lombardia.
# Addizionale comunale: 0.80% with soglia 12 000 EUR.
p = compute(
    PayrollScenario(
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
            calculation_date=date(2026, 1, 1),
        ),
    )
)

print(f"Net annual (no addizionali):    {baseline.net_annual} EUR")
print(f"Net annual (with addizionali):  {p.net_annual} EUR")
print(f"Addizionale regionale:          {p.addizionale_regionale_annual} EUR")
print(f"Addizionale comunale:           {p.addizionale_comunale_annual} EUR")

# When addizionali are computed they are no longer in fiscal_simplifications.
assert FiscalSimplification.NO_ADDIZIONALE_REGIONALE not in p.fiscal_simplifications
assert FiscalSimplification.NO_ADDIZIONALE_COMUNALE not in p.fiscal_simplifications
assert p.addizionale_regionale_annual > Decimal(0)
assert p.addizionale_comunale_annual > Decimal(0)
