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
matches to the cent.  The deductions differ: the payroll prints 1,621.58
EUR, the engine gives 1,606.30 for the 243 days from 1 January to 31
August (the art. 13 deduction and the ulteriore detrazione, each
proportioned to the days).  No whole number of days gives the printed
figure (245 days give 1,619.52, 246 give 1,626.12) and the payslip prints
neither the days nor the split, so the cause is not known; decision: keep
the statutory computation and record the 15.28 EUR as unexplained.
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


def test_annual_deductions_of_p25_differ_by_an_unexplained_amount() -> None:
    """243 days: 1,606.30 against the 1,621.58 the payroll prints."""
    rules = load_year_rules(2026, TaxSector.TERZIARIO, 10)
    taxable = Decimal("33014.13")
    assert rules.ulteriore_detrazione is not None
    deductions = work_income_deduction(
        taxable, 243, rules.work_deduction
    ) + ulteriore_detrazione_lavoro(taxable, rules.ulteriore_detrazione, 243)

    assert deductions == Decimal("1606.30")
    assert Decimal("1621.58") - deductions == Decimal("15.28")
