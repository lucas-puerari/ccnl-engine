"""FSBA: a solidarity fund by headcount on top of the artigianato rates.

Regolamento FSBA of 11 September 2024 art. 3 (sha256
c345db470ee7a3427e302419a59ed5ce0733502b6a597c9f46fd5df37944b3db): 0.60%
of the INPS taxable pay up to 15 employees, 1.00% above, three quarters
employer and one quarter worker; art. 1 binds every artigianato employer,
so fixed-term workers are charged too.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import list_contracts, load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.inputs import FixedTerm
from ccnl_engine.fund.solidarity.models import (
    SolidarityFund,
    SolidarityTier,
    with_solidarity_headcount,
)
from ccnl_engine.fund.solidarity.services import (
    EMPLOYEE_COMPONENT,
    EMPLOYER_COMPONENT,
)
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_CCNL = "metalmeccanico-artigianato"


def _run(headcount: int, **kwargs: object) -> PeriodResult:
    level = load_ccnl(_CCNL).levels[0].code
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id=_CCNL,
            level_code=level,
            employer=EmployerProfile(headcount=Headcount(headcount)),
            opening_state=PeriodState.zero(),
            tfr_treasury_fund=False,
            **kwargs,  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _rates(result: PeriodResult) -> tuple[Decimal, Decimal]:
    components = {c.name: c for c in result.contribution_breakdown.components}
    return components[EMPLOYER_COMPONENT].rate, components[EMPLOYEE_COMPONENT].rate


@pytest.mark.parametrize(
    ("headcount", "employer", "employee"),
    [(15, "0.0045", "0.0015"), (16, "0.0075", "0.0025")],
)
def test_the_tier_follows_the_headcount(
    headcount: int, employer: str, employee: str
) -> None:
    """Up to 15 employees 0.60%, above 1.00%, split three quarters to one."""
    assert _rates(_run(headcount)) == (Decimal(employer), Decimal(employee))


def test_a_fixed_term_worker_is_charged() -> None:
    """Art. 1 binds the employer for every employee, fixed terms included."""
    result = _run(5, contract_type=FixedTerm())

    assert _rates(result) == (Decimal("0.0045"), Decimal("0.0015"))


def test_every_artigianato_ccnl_has_the_fund() -> None:
    """The eight CCNL of the INPS artigianato sector charge FSBA."""
    artisans = [
        str(c.ccnl_id)
        for c in list_contracts()
        if load_ccnl(str(c.ccnl_id)).meta.tax_sector == "artigianato"
    ]
    assert len(artisans) == 8
    for ccnl_id in artisans:
        fund = load_ccnl(ccnl_id).parameters.solidarity_fund
        assert fund is not None
        assert fund.code == "FSBA"
        assert fund.covers_fixed_term


def test_a_fund_without_top_up_tiers_is_left_as_it_is() -> None:
    """Only a fund on top of the sector rates by headcount is resolved."""
    ccnl = load_ccnl("bancari-abi")

    assert with_solidarity_headcount(ccnl, 50) is ccnl


def test_two_shapes_are_rejected() -> None:
    """A fund is flat, in place of the FIS or on top by headcount, never two."""
    fund = load_ccnl(_CCNL).parameters.solidarity_fund
    assert fund is not None
    tiers = fund.top_up_tiers
    with pytest.raises(ValidationError, match="either an employer"):
        SolidarityFund(
            code="X",
            top_up_tiers=tiers,
            wage_integration_tiers=tiers,
            provenance=fund.provenance,
        )


def test_top_up_tiers_need_one_open_tier() -> None:
    """Every headcount must fall in a tier."""
    fund = load_ccnl(_CCNL).parameters.solidarity_fund
    assert fund is not None
    bounded = (
        SolidarityTier(
            max_employees=15,
            employer_rate=Decimal("0.0045"),
            employee_rate=Decimal("0.0015"),
        ),
    )
    with pytest.raises(ValidationError, match="exactly one open tier"):
        SolidarityFund(code="X", top_up_tiers=bounded, provenance=fund.provenance)


def test_a_flat_fund_keeps_its_rates_whatever_the_headcount() -> None:
    """``for_headcount`` changes only a fund on top by headcount."""
    fund = load_ccnl("bancari-abi").parameters.solidarity_fund
    assert fund is not None

    assert fund.for_headcount(3) is fund
