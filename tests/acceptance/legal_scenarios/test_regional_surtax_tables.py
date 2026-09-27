"""Regional surtax of the 2026 conguaglio on the MEF 2026 tables.

Commercio L4, employed since 2020 and computed by the engine for 2026, no
municipality.  The expected amounts are computed below from the MEF
Dipartimento delle Finanze pages retrieved on 27 September 2026, on the
annual taxable income the conguaglio reports:

- Lombardia, https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/
  fiscalitalocale/addregirpef/addregirpef.php?reg=10&anno=2026: 1.23% up to
  15,000, 1.58% up to 28,000, 1.72% up to 50,000, 1.73% above (L.R. 10/2003
  art. 72 c. 1);
- Veneto, ``...addregirpef.php?reg=21&anno=2026``: 1.23% aliquota unica;
  0.9% for a taxpayer with a disability or with a dependent family member
  with a disability, up to 50,000 (L.R. 19/2005 art. 1 c. 5).  The engine
  does not apply that rate: with a dependent child declared the result is
  provisional and names the provision.

Both surtaxes are due only when net IRPEF is due (D.Lgs. 446/1997 art. 50
c. 2); the IRPEF oracle confirms it is.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from functools import cache
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    CalculationStatus,
    Dependent,
    DependentRelationship,
    EmployerProfile,
    Employment,
    EmploymentPeriod,
    FamilyComposition,
    Headcount,
    PayrollEngine,
    PeriodFacts,
    YearInput,
)
from tests.fixtures.legal_examples.irpef_2026 import net_irpef

if TYPE_CHECKING:
    from ccnl_engine import CalculationDecision, PeriodResult

pytestmark = pytest.mark.legal_scenario

_ENGINE = PayrollEngine.bundled()
_CENT = Decimal("0.01")
_LOMBARDIA = (
    (Decimal(15_000), Decimal("0.0123")),
    (Decimal(28_000), Decimal("0.0158")),
    (Decimal(50_000), Decimal("0.0172")),
    (None, Decimal("0.0173")),
)
_VENETO_RATE = Decimal("0.0123")
_CHILD = FamilyComposition(
    dependents=(Dependent(relationship=DependentRelationship.CHILD),)
)


def _marginal(
    taxable: Decimal, brackets: tuple[tuple[Decimal | None, Decimal], ...]
) -> Decimal:
    tax = Decimal(0)
    lower = Decimal(0)
    for upper, rate in brackets:
        top = taxable if upper is None else min(taxable, upper)
        if top > lower:
            tax += (top - lower) * rate
        if upper is not None:
            lower = upper
    return tax.quantize(_CENT, rounding=ROUND_HALF_UP)


@cache
def _conguaglio(regione: str, with_child: bool) -> PeriodResult:
    result = _ENGINE.calculate_year(
        YearInput(
            year=2026,
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                employment_period=EmploymentPeriod(date(2020, 1, 1), None),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            default_facts=PeriodFacts(
                regione=regione, family_composition=_CHILD if with_child else None
            ),
        )
    )
    return result.period_results[-1]


def _regional(result: PeriodResult) -> CalculationDecision:
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "addizionale_regionale" and "component" not in d.inputs
    )
    return decision


def _taxable(decision: CalculationDecision) -> Decimal:
    taxable = decision.inputs["taxable_income"]
    assert isinstance(taxable, Decimal)
    assert net_irpef(taxable) > 0
    return taxable


def test_lombardia_applies_the_2026_brackets() -> None:
    """Lombardia: the four MEF 2026 brackets on the conguaglio income, final."""
    result = _conguaglio("IT-25", with_child=False)
    decision = _regional(result)

    assert decision.reason_code == "table_applied"
    assert decision.status is CalculationStatus.FINAL
    assert decision.amount == _marginal(_taxable(decision), _LOMBARDIA)
    assert "regional_surtax_dependent_provisions_not_applied" not in {
        i.code for i in result.issues
    }


def test_veneto_with_a_child_is_provisional() -> None:
    """Veneto: 1.23% on the whole income; the disability rate is not applied."""
    result = _conguaglio("IT-34", with_child=True)
    decision = _regional(result)

    expected = (_taxable(decision) * _VENETO_RATE).quantize(
        _CENT, rounding=ROUND_HALF_UP
    )
    assert decision.reason_code == "dependent_provisions_not_applied"
    assert decision.amount == expected
    assert decision.status is CalculationStatus.PROVISIONAL
    assert "regional_surtax_dependent_provisions_not_applied" in {
        i.code for i in result.issues
    }
    assert result.status is CalculationStatus.PROVISIONAL
