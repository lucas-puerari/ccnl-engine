"""The engine against payslips of real payrolls: every difference recorded.

The oracles of this test suite are written from the statutes by the same
hand that wrote the data, so they cannot catch a misreading the two share.
The payslips of ``observed_payslip/`` come from payroll software of real
employers: they are an independent result.  Each comparison below states
what matched and every difference, with its cause and the decision taken.

Monthly: the FIS share of the worker.  Payroll software charges one third
of the FIS rate to five decimals of a percentage point ("FIS D.Lgs.
148/2015 fino 15 dipendenti ... 0,26667": p09, January 2026; p10), and
with the CIGS above fifteen employees (p15: FIS 0,2667 and CIGS 0,30).
The bundle rounded the third to 0.27 until 14 October 2026, 0.08 EUR too
much on 2,430 EUR; the shares are now exact (decision: follow the statute,
D.Lgs. 148/2015 art. 33 c. 1, as the payrolls do).

Annual: the conguaglio of a termination in August 2026 (p25, Terziario
level 3).  The gross IRPEF of the printed annual taxable, 8,094.66 EUR,
matches to the cent.  The deductions, 1,621.58 EUR, are explained: the
payroll counts the 242 days it prints (gg_detrazioni), proportions the art.
13 deduction and the ulteriore detrazione (578.96) to them, and adds the 65
EUR of art. 13 c. 1.1 whole (circolare AdE 4/E/2022, par. 1.2.1: "senza
effettuare alcun ragguaglio al periodo di lavoro nell'anno").  The printed
split confirms it: other_deductions 1,042.62 = 977.62 + 65.

Decision ``engine_bug``: the engine proportioned the 65 EUR too, 15.28 EUR
less on this payslip; fixed, with this test as regression.  One cent stays,
decision ``accepted_external_variance``: 1,474.52 * 242 / 365 is 977.6267,
the engine rounds it to 977.63 and the payroll prints 977.62.  No source
states how the proportioned deduction is rounded; the engine keeps
half-up, and the comparison tolerance is one cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.agreement.facade import TaxSector
from ccnl_engine.irpef.deduction.rules import work_income_deduction
from ccnl_engine.irpef.rules import irpef_gross
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.sector.loaders import load_year_rules
from ccnl_engine.tax_credit.rules import ulteriore_detrazione_lavoro

pytestmark = pytest.mark.legal_scenario


def _worker_share(headcount: int) -> Decimal:
    """Return the non-IVS share of the terziario worker at ``headcount``.

    Returns:
        The FIS share, plus the CIGS share above fifteen employees.
    """
    inps = load_year_rules(2026, TaxSector.TERZIARIO, headcount).inps
    assert inps is not None
    return inps.employee_rate - inps.employee_ivs_rate


@pytest.mark.parametrize(
    ("payslip", "headcount", "base", "printed"),
    [
        ("p09", 10, "1016.00", "2.71"),
        ("p10", 10, "1698.00", "4.53"),
        ("p15", 20, "2387.00", "13.53"),
    ],
)
def test_the_worker_share_is_the_one_payrolls_print(
    payslip: str, headcount: int, base: str, printed: str
) -> None:
    """FIS 0.26667%, plus the CIGS 0.30% above fifteen employees."""
    assert money(Decimal(base) * _worker_share(headcount)) == Decimal(printed), payslip


def test_annual_gross_irpef_matches_the_conguaglio_of_p25() -> None:
    """33,014.13 of annual taxable: 8,094.66 of gross IRPEF, as printed."""
    rules = load_year_rules(2026, TaxSector.TERZIARIO, 10)

    assert irpef_gross(Decimal("33014.13"), rules) == Decimal("8094.66")


def test_annual_deductions_match_the_conguaglio_of_p25() -> None:
    """242 days: 977.63 + 65 + 578.96 = 1,621.59, the printed 1,621.58 to a cent."""
    rules = load_year_rules(2026, TaxSector.TERZIARIO, 10)
    taxable = Decimal("33014.13")
    assert rules.ulteriore_detrazione is not None
    work = work_income_deduction(taxable, 242, rules.work_deduction)
    ulteriore = ulteriore_detrazione_lavoro(taxable, rules.ulteriore_detrazione, 242)

    assert work == Decimal("1042.63")
    assert ulteriore == Decimal("578.96")
    assert abs(work + ulteriore - Decimal("1621.58")) <= Decimal("0.01")
