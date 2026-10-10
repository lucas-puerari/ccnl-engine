"""Compensations of the TFR conferred outside the company, on one run.

D.Lgs. 252/2005 art. 10 c. 2 exempts the employer from the Fondo di
garanzia TFR contribution (0.20%, 0.40% for the dirigenti industriali) and
c. 3, with D.L. 203/2005 art. 8 and its Tabella A, from 0.28 points of the
social contributions, in the percentage of the TFR conferred to a pension
fund or to the Fondo Tesoreria (INPS circ. 70/2007 par. 6, circ. 4/2008).
"""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.payroll.contribution.results import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.payroll.contribution.services import TfrAccrual
from ccnl_engine.payroll.contribution.services_tfr_compensation import (
    GUARANTEE_FUND_COMPONENT,
    RELIEF_COMPONENT,
    with_tfr_compensation,
)
from ccnl_engine.payroll.employment.inputs import Apprentice, Permanent
from ccnl_engine.tax.severance.models import TfrCompensation, TfrRules
from tests.unit.ccnl_engine.builders import make_year_rules

if TYPE_CHECKING:
    from ccnl_engine.payroll.amount.types import _AmountsInput

_COMPENSATION = TfrCompensation(
    guarantee_fund_rate=Decimal("0.0020"),
    guarantee_fund_rate_by_category={WorkerCategory.DIRIGENTE: Decimal("0.0040")},
    relief_rate=Decimal("0.0028"),
)
_CONFERRED = TfrAccrual(quota=Decimal("130.64"), to_pension_fund=True)
_BASE = Decimal(1764)


def _input(
    *,
    compensation: TfrCompensation | None = _COMPENSATION,
    contract: Permanent | Apprentice | None = None,
    category: WorkerCategory | None = WorkerCategory.OPERAIO,
) -> _AmountsInput:
    rules = make_year_rules()
    tfr = TfrRules(accrual_divisor=Decimal("13.5"), compensation=compensation)
    return cast(
        "_AmountsInput",
        SimpleNamespace(
            rules=rules.model_copy(update={"tfr": tfr}),
            contract_type=contract or Permanent(),
            category=category,
        ),
    )


def _breakdown(
    employer: Decimal = Decimal("541.15"),
    names: tuple[str, ...] = ("non_ivs_employer",),
) -> ContributionBreakdown:
    components = tuple(
        ContributionComponent(name, _BASE, Decimal("0.07"), Decimal("123.48"))
        for name in names
    )
    return ContributionBreakdown(Decimal(162), employer, components)


def _credits(breakdown: ContributionBreakdown) -> dict[str, Decimal]:
    return {c.name: c.amount for c in breakdown.components if c.amount < 0}


def test_conferred_tfr_cuts_the_fund_rate_and_the_relief_points() -> None:
    """On 1764: Fondo di garanzia 3.53 and art. 8 relief 4.94."""
    result = with_tfr_compensation(_input(), _breakdown(), _CONFERRED)
    assert _credits(result) == {
        GUARANTEE_FUND_COMPONENT: Decimal("-3.53"),
        RELIEF_COMPONENT: Decimal("-4.94"),
    }
    assert result.employer == Decimal("541.15") - Decimal("8.47")
    exemption = next(c for c in result.components if c.name == RELIEF_COMPONENT)
    assert (exemption.base, exemption.rate) == (_BASE, Decimal("-0.0028"))


def test_dirigente_takes_the_rate_of_the_category() -> None:
    """A dirigente industriale pays, and is exempted from, 0.40%: 7.06."""
    inp = _input(category=WorkerCategory.DIRIGENTE)
    result = with_tfr_compensation(inp, _breakdown(), _CONFERRED)
    assert _credits(result)[GUARANTEE_FUND_COMPONENT] == Decimal("-7.06")


def test_worker_without_category_takes_the_general_rate() -> None:
    """No category: the 0.20% of the sector."""
    result = with_tfr_compensation(_input(category=None), _breakdown(), _CONFERRED)
    assert _credits(result)[GUARANTEE_FUND_COMPONENT] == Decimal("-3.53")


def test_apprentice_takes_the_relief_only() -> None:
    """The Fondo di garanzia share of an apprentice is not sourced."""
    inp = _input(contract=Apprentice(months_elapsed=0))
    result = with_tfr_compensation(inp, _breakdown(), _CONFERRED)
    assert _credits(result) == {RELIEF_COMPONENT: Decimal("-4.94")}


@pytest.mark.parametrize(
    ("employer", "fund", "relief"),
    [(Decimal("5.00"), "-3.53", "-1.47"), (Decimal("2.00"), "-2.00", "0.00")],
)
def test_credit_never_exceeds_the_employer_contributions(
    employer: Decimal, fund: str, relief: str
) -> None:
    """The exemptions take what the run owes, the Fondo di garanzia first."""
    result = with_tfr_compensation(_input(), _breakdown(employer), _CONFERRED)
    assert result.employer == 0
    amounts = {c.name: c.amount for c in result.components}
    assert amounts[GUARANTEE_FUND_COMPONENT] == Decimal(fund)
    assert amounts[RELIEF_COMPONENT] == Decimal(relief)


@pytest.mark.parametrize(
    "accrual",
    [
        TfrAccrual(quota=Decimal("130.64")),
        TfrAccrual(quota=Decimal("130.64"), treasury_fund=None),
    ],
)
def test_tfr_kept_or_unknown_takes_no_compensation(accrual: TfrAccrual) -> None:
    """Kept in the company, or a Fondo Tesoreria destination not stated."""
    breakdown = _breakdown()
    assert with_tfr_compensation(_input(), breakdown, accrual) is breakdown


def test_sector_without_compensation_rule_is_unchanged() -> None:
    """Domestic work, public administrations and agricoltura have none."""
    breakdown = _breakdown()
    inp = _input(compensation=None)
    assert with_tfr_compensation(inp, breakdown, _CONFERRED) is breakdown


def test_base_falls_back_to_the_ivs_component() -> None:
    """A sector with no non-IVS employer rate exempts on the IVS base."""
    result = with_tfr_compensation(
        _input(), _breakdown(names=("ivs_employer",)), _CONFERRED
    )
    assert _credits(result)[RELIEF_COMPONENT] == Decimal("-4.94")


def test_run_without_employer_base_is_unchanged() -> None:
    """No employer component, no base: nothing to exempt."""
    breakdown = _breakdown(names=("ivs_employee",))
    assert with_tfr_compensation(_input(), breakdown, _CONFERRED) is breakdown
