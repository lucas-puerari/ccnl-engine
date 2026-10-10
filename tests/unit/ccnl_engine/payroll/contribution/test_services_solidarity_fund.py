"""Ordinary contribution of the solidarity fund of the CCNL on one run.

INPS circ. 90/2015 p. 11: the credito fund charges 0.20% (0.133% employer,
0.067% worker) on the INPS taxable pay of every permanent worker,
dirigenti included; an apprenticeship is a permanent contract (D.Lgs.
81/2015 art. 41 c. 1).
"""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.contract.fund.models_solidarity import SolidarityFund
from ccnl_engine.payroll.contribution.results import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.payroll.contribution.services_solidarity_fund import (
    EMPLOYEE_COMPONENT,
    EMPLOYER_COMPONENT,
    with_solidarity_fund,
)
from ccnl_engine.payroll.employment.inputs import Apprentice, FixedTerm, Permanent
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.provenance.source.models_chain import ProvenanceStatus, RuleProvenance

if TYPE_CHECKING:
    from ccnl_engine.payroll.amount.types import _AmountsInput

_FUND = SolidarityFund(
    code="FONDO_SOLIDARIETA_CREDITO",
    employer_rate=Decimal("0.00133"),
    employee_rate=Decimal("0.00067"),
    provenance=RuleProvenance(
        status=ProvenanceStatus.DERIVED,
        location=SourceLocation(
            source_document=SourceDocument(
                document_id="inps-circolare-90-2015",
                title="INPS Circolare n. 90 del 6 maggio 2015",
                kind=SourceKind.INPS_CIRCOLARE,
            ),
        ),
    ),
)
_BASE = Decimal(3200)


def _input(
    contract: Permanent | Apprentice | FixedTerm, fund: SolidarityFund | None = _FUND
) -> _AmountsInput:
    return cast(
        "_AmountsInput", SimpleNamespace(solidarity_fund=fund, contract_type=contract)
    )


def _breakdown(name: str = "non_ivs_employer") -> ContributionBreakdown:
    component = ContributionComponent(name, _BASE, Decimal("0.03"), Decimal(96))
    return ContributionBreakdown(Decimal(294), Decimal(856), (component,))


@pytest.mark.parametrize("contract", [Permanent(), Apprentice(months_elapsed=0)])
def test_permanent_worker_pays_the_ordinary_contribution(
    contract: Permanent | Apprentice,
) -> None:
    """On 3,200: employer 4.256 -> 4.26, worker 2.144 -> 2.14."""
    result, rate = with_solidarity_fund(_input(contract), _breakdown())
    amounts = {c.name: c.amount for c in result.components}
    assert amounts[EMPLOYER_COMPONENT] == Decimal("4.26")
    assert amounts[EMPLOYEE_COMPONENT] == Decimal("2.14")
    assert (result.employer, result.employee) == (Decimal("860.26"), Decimal("296.14"))
    assert rate == Decimal("0.00067")


def test_base_falls_back_to_the_ivs_component() -> None:
    """A sector with no non-IVS employer rate charges on the IVS base."""
    result, _ = with_solidarity_fund(_input(Permanent()), _breakdown("ivs_employer"))
    assert {c.name: c.base for c in result.components}[EMPLOYEE_COMPONENT] == _BASE


def test_run_without_employer_base_charges_nothing() -> None:
    """No employer component: a zero base and zero contribution."""
    result, _ = with_solidarity_fund(_input(Permanent()), _breakdown("ivs_employee"))
    assert result.employer == Decimal(856)


@pytest.mark.parametrize(
    "inp",
    [
        _input(FixedTerm()),
        _input(Permanent(), fund=None),
    ],
)
def test_fixed_term_or_ccnl_without_fund_is_unchanged(inp: _AmountsInput) -> None:
    """The fund charges permanent contracts of the CCNLs that have one."""
    breakdown = _breakdown()
    assert with_solidarity_fund(inp, breakdown) == (breakdown, Decimal(0))
