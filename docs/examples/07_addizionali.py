"""Regional and municipal IRPEF surcharges (addizionali).

By default the engine omits addizionale regionale and comunale
(they appear in fiscal_simplifications). Pass a SurtaxRules object
and set regione / comune_belfiore in the Scenario to include them.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    FiscalSimplification,
    Permanent,
    Scenario,
    compute,
    load_ccnl,
    load_year_rules,
)
from ccnl_engine.surtax.loaders import load_surtax_rules

ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)
surtax = load_surtax_rules(2026)

# Baseline: no surtax argument → addizionali are zero.
baseline = compute(
    ccnl,
    rules,
    Scenario(
        level_code="4",
        as_of=date(2026, 1, 1),
        employment=Permanent(),
        num_employees=50,
    ),
)

# Worker resident in Romano di Lombardia (codice belfiore H509), Lombardia.
# Addizionale comunale: 0.80% with soglia 12 000 EUR.
scenario = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
    regione="Lombardia",
    comune_belfiore="H509",  # Romano di Lombardia
)

p = compute(ccnl, rules, scenario, surtax=surtax)

print(f"Net annual (no addizionali):    {baseline.net_annual} EUR")
print(f"Net annual (with addizionali):  {p.net_annual} EUR")
print(f"Addizionale regionale:          {p.addizionale_regionale_annual} EUR")
print(f"Addizionale comunale:           {p.addizionale_comunale_annual} EUR")

# When addizionali are computed they are no longer in fiscal_simplifications.
assert FiscalSimplification.NO_ADDIZIONALE_REGIONALE not in p.fiscal_simplifications
assert FiscalSimplification.NO_ADDIZIONALE_COMUNALE not in p.fiscal_simplifications
assert p.addizionale_regionale_annual > Decimal(0)
assert p.addizionale_comunale_annual > Decimal(0)
