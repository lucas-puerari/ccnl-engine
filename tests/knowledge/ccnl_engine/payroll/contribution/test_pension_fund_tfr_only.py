"""A worker who confers the TFR alone, with no contribution of either side.

D.Lgs. 252/2005 art. 8 c. 1: the fund is financed by the worker, the
employer and the TFR; the Schede of the funds give the "facoltà di
versamento del solo trattamento di fine rapporto senza contribuzione del
lavoratore e del datore", for the private employees alone (Perseo Sirio).
Previambiente art. 65 c. 12: the 10 EUR of c. 11 are owed "anche [...] ai
lavoratori che aderiscono al Fondo a seguito di conferimento [...] del
solo TFR", beside the 5 EUR insurance of c. 13.

- Commercio 4 in January 2026, Fon.Te.: nothing of either side, the TFR
  paid to the fund.
- Servizi ambientali Q in March 2026, Previambiente, permanent: 10 + 5 =
  15.00 employer, no employee part, no conventional base needed.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment, InvalidInputError
from ccnl_engine.inputs import EmploymentPeriod, PensionFundEnrolment, Permanent
from tests.knowledge.ccnl_engine.payroll.employment.builders_seniority import new_hire
from tests.knowledge.ccnl_engine.payroll.support import regular_period
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def _run(slug: str, level: str, fund: str, month: int = 1) -> PeriodResult:
    employment = Employment(
        ccnl_slug=slug,
        level_code=level,
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2026, 1, 1)),
        pension_fund=PensionFundEnrolment(fund, Decimal(0), tfr_to_fund=True),
        contract_type=Permanent(),
    )
    return regular_period(
        employment=employment, month=month, current_year=employment_only()
    )


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def test_no_contribution_and_the_tfr_paid() -> None:
    """Fon.Te.: no employer or employee part, the TFR goes to the fund."""
    result = _run("commercio-confcommercio.json", "4", "FONTE")
    assert _entry(result, "pension_fund_employer") == 0
    assert _entry(result, "pension_fund_employee") == 0
    assert _entry(result, "pension_fund_tfr") > 0
    assert _entry(result, "tfr_accrual") == 0


def test_previambiente_owes_its_contractual_contribution() -> None:
    """C. 12: 10 + 5 = 15.00, no rates, no conventional base needed."""
    result = _run("igiene-ambientale-utilitalia.json", "Q", "PREVIAMBIENTE", 3)
    assert _entry(result, "pension_fund_employer") == Decimal("15.00")
    assert _entry(result, "pension_fund_employee") == 0
    codes = {i.code for i in result.issues}
    assert "pension_fund_conventional_base_unknown" not in codes


def test_public_employee_cannot_confer_the_tfr_alone() -> None:
    """Perseo Sirio: the TFR alone is for the private employees only."""
    with pytest.raises(InvalidInputError, match="TFR alone"):
        _run("funzioni-centrali-aran.json", "FUNZIONARI", "PERSEO_SIRIO")
