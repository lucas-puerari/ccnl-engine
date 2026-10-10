"""Credit for foreign taxes: LIMITE 1 per State, LIMITE 2 on the total.

Art. 165 c. 1 and 3 TUIR, circ. AdE 9/E/2015 par. 3.1.  Every case has an
imposta lorda of 10,000.00 EUR, deductions of 3,000.00 EUR (imposta netta
7,000.00 EUR) and a taxable income of 40,000.00 EUR.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.payroll.domain.foreign_tax import ForeignTaxPaid
from ccnl_engine.payroll.service.foreign_tax_credit import (
    foreign_credit_rule,
    foreign_tax_credit,
)
from ccnl_engine.payroll.service.irpef_net import NetIrpef
from ccnl_engine.tax.annual.loaders import load_year_rules

_RULES = load_year_rules(2026, TaxSector.INDUSTRIA, 50)
_TAXABLE = Decimal(40000)
_ANNUAL = NetIrpef(
    gross=Decimal(10000),
    work_deduction=Decimal(3000),
    family_deductions=Decimal(0),
    ulteriore=None,
)


def _paid(country: str, income: int, tax: int) -> ForeignTaxPaid:
    return ForeignTaxPaid(country, Decimal(income), Decimal(tax))


def test_no_foreign_tax_no_credit() -> None:
    """Without foreign taxes there is no credit and no decision."""
    assert foreign_tax_credit((), _TAXABLE, _ANNUAL, _RULES) is None


@pytest.mark.parametrize(
    ("paid", "credit"),
    [
        # Quota 10,000 x 10,000 / 40,000 = 2,500; tax 1,000 below it.
        (_paid("FR", 10000, 1000), Decimal(1000)),
        # Tax 3,000 above the quota of 2,500: LIMITE 1.
        (_paid("FR", 10000, 3000), Decimal("2500.00")),
        # Income above the taxable: the ratio is 1, quota 10,000; LIMITE 2
        # caps it at the imposta netta of 7,000.
        (_paid("FR", 50000, 9000), Decimal(7000)),
    ],
)
def test_one_state(paid: ForeignTaxPaid, credit: Decimal) -> None:
    """The credit is the lower of the tax and the quota, within the netta."""
    result = foreign_tax_credit((paid,), _TAXABLE, _ANNUAL, _RULES)
    assert result is not None
    assert result.amount == credit
    assert result.decision.capability == "foreign_tax_credit"


def test_states_are_limited_separately_then_on_the_netta() -> None:
    """FR: min(3,000, 2,500) = 2,500; DE: min(6,000, 5,000) = 5,000.

    Together 7,500 above the imposta netta of 7,000: the credit is 7,000.
    """
    result = foreign_tax_credit(
        (_paid("FR", 10000, 3000), _paid("DE", 20000, 6000)),
        _TAXABLE,
        _ANNUAL,
        _RULES,
    )
    assert result is not None
    assert result.amount == Decimal(7000)
    decision = result.decision
    assert decision.reason_code == "limited_to_net_tax"
    assert decision.inputs["fr_quota"] == Decimal("2500.00")
    assert decision.inputs["de_credit"] == Decimal("5000.00")


def test_no_taxable_income_no_quota() -> None:
    """Without taxable income there is no Italian tax to credit against."""
    zero = NetIrpef(Decimal(0), Decimal(0), Decimal(0), None)
    result = foreign_tax_credit((_paid("FR", 100, 10),), Decimal(0), zero, _RULES)
    assert result is not None
    assert result.amount == Decimal(0)
    assert result.decision.reason_code == "credit_applied"


def test_credit_lowers_the_net_irpef() -> None:
    """The net IRPEF is the imposta netta less the credit."""
    annual = NetIrpef(
        _ANNUAL.gross,
        _ANNUAL.work_deduction,
        _ANNUAL.family_deductions,
        None,
        foreign_credit=Decimal(2500),
    )
    assert annual.net_before_credit == Decimal(7000)
    assert annual.net == Decimal(4500)


@pytest.mark.parametrize(
    ("tax_year", "rule", "citation"),
    [
        (2026, "tuir-art165-c1", "Art. 165 TUIR"),
        (2027, "dlgs117-2026-art185-c1", "Art. 185 D.Lgs. 117/2026"),
    ],
)
def test_rule_follows_the_norm_in_force(
    tax_year: int, rule: str, citation: str
) -> None:
    """Art. 165 TUIR until 2026, art. 185 D.Lgs. 117/2026 from 2027.

    Normattiva, accessed 2026-10-09: art. 185 of the testo unico, "Credito
    d'imposta per i redditi prodotti all'estero (articolo 165 decreto del
    Presidente della Repubblica 22 dicembre 1986, n. 917)", c. 1 unchanged.
    """
    assert foreign_credit_rule(tax_year) == (rule, citation)
