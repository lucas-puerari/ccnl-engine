"""Decision on the art. 13 minimum the withholding leaves to the tax return.

Istruzioni per la compilazione della Certificazione Unica 2026, Agenzia delle
Entrate, updated 24 February 2026, punto 367, p. 33: for an employment
shorter than the year "il sostituto deve ragguagliare anche la detrazione
minima al periodo di lavoro" and tells the worker, code AN (Tabella F, p.
93), that the tax return grants "la detrazione per l'intero anno".
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.service.irpef_minimum import (
    MINIMUM_PROPORTIONED,
    minimum_decision,
)
from ccnl_engine.tax.annual.loaders import load_year_rules

_RULES = load_year_rules(2026, TaxSector.INDUSTRIA, 50)
_FLAT_BAND = Decimal(10_000)


@pytest.mark.parametrize(
    ("fixed_term", "contract", "minimum", "balance"),
    [
        # 1,955 * 92 / 365 = 492.77; 690 - 492.77 = 197.23.
        pytest.param(False, "open_ended", Decimal(690), Decimal("197.23"), id="open"),
        # 1,380 - 492.77 = 887.23.
        pytest.param(True, "fixed_term", Decimal(1380), Decimal("887.23"), id="fixed"),
    ],
)
def test_short_employment_records_the_balance_of_the_tax_return(
    *, fixed_term: bool, contract: str, minimum: Decimal, balance: Decimal
) -> None:
    """Income 10,000 EUR over 92 days: the minimum exceeds 492.77."""
    decision = minimum_decision(_RULES, _FLAT_BAND, 92, fixed_term=fixed_term)

    assert decision is not None
    assert decision.capability == "irpef"
    assert decision.status is CalculationStatus.FINAL
    assert decision.reason_code == MINIMUM_PROPORTIONED
    assert decision.amount is None
    assert decision.inputs["contract"] == contract
    assert decision.inputs["eligible_work_days"] == "92"
    assert decision.inputs["minimum"] == minimum
    assert decision.inputs["tax_return_balance"] == balance
    assert decision.source is not None
    assert decision.source.page == "33"


@pytest.mark.parametrize(
    ("income", "days"),
    [
        pytest.param(_FLAT_BAND, 365, id="full-year"),
        pytest.param(Decimal(20_000), 30, id="above-flat-band"),
        pytest.param(Decimal(0), 92, id="no-income"),
    ],
)
def test_no_decision_without_a_balance(income: Decimal, days: int) -> None:
    """A full year deducts 1,955; above 15,000 or without income no minimum."""
    assert minimum_decision(_RULES, income, days, fixed_term=True) is None
