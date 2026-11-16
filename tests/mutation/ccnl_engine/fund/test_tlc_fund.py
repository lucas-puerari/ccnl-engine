"""The Fondo TLC by the INPS sector of the employer and by date.

D.I. 4 agosto 2023 art. 7: every enterprise pays 0.45% (two thirds employer),
one outside the CIGO also 0.80% in place of the FIS and CIGS, on the
permanent workers and apprentices, not the dirigenti; D.I. 1 settembre 2026:
the 0.45% becomes 0.75% from February 2027.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.fund.solidarity.coverage import fund_covers
from ccnl_engine.fund.solidarity.models import select_solidarity_fund
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FixedTerm,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)

if TYPE_CHECKING:
    from ccnl_engine.fund.solidarity.models import SolidarityFund
    from ccnl_engine.period.requests import PeriodCalculationRequest

_CCNL = load_ccnl("telecomunicazioni-asstel")


def _in(sector: TaxSector, day: date) -> SolidarityFund | None:
    ccnl = _CCNL.model_copy(
        update={"meta": _CCNL.meta.model_copy(update={"tax_sector": sector})}
    )
    return select_solidarity_fund(ccnl, day).parameters.solidarity_fund


@pytest.mark.parametrize(
    ("day", "employer", "employee"),
    [
        (date(2026, 6, 1), Decimal("0.003"), Decimal("0.0015")),
        (date(2027, 2, 1), Decimal("0.005"), Decimal("0.0025")),
    ],
)
def test_an_employer_in_the_cigo_pays_the_rate_of_every_enterprise(
    day: date, employer: Decimal, employee: Decimal
) -> None:
    """0.45% on top of the sector rates, 0.75% from February 2027."""
    fund = _in(TaxSector.INDUSTRIA, day)
    assert fund is not None
    assert (fund.employer_rate, fund.employee_rate) == (employer, employee)
    assert not fund.covers_fixed_term
    assert not fund.covers_executives


@pytest.mark.parametrize(
    ("day", "employer"),
    [
        (date(2026, 6, 1), Decimal("0.0083333333")),
        (date(2027, 2, 1), Decimal("0.0103333333")),
    ],
)
def test_an_employer_outside_the_cigo_pays_in_place_of_the_fis(
    day: date, employer: Decimal
) -> None:
    """0.80% + 0.45% = 1.25%, then 1.55%, in place of the FIS and CIGS."""
    fund = _in(TaxSector.TERZIARIO, day)
    assert fund is not None
    (tier,) = fund.wage_integration_tiers
    assert tier.employer_rate == employer
    assert fund.wage_integration_permanent_only


def test_no_fund_before_the_decree() -> None:
    """The fund starts in January 2024."""
    assert _in(TaxSector.INDUSTRIA, date(2023, 12, 1)) is None


def test_the_fund_in_place_of_the_fis_charges_only_the_permanent_workers() -> None:
    """A fixed term or a dirigente is not charged; a permanent worker is."""
    fund = _in(TaxSector.TERZIARIO, date(2026, 6, 1))

    def request(contract: object, category: object) -> PeriodCalculationRequest:
        return cast(
            "PeriodCalculationRequest",
            SimpleNamespace(contract_type=contract, category=category),
        )

    assert fund_covers(fund, request(Permanent(), None))
    assert not fund_covers(fund, request(FixedTerm(), None))
    assert not fund_covers(fund, request(Permanent(), WorkerCategory.DIRIGENTE))
    assert fund_covers(None, request(FixedTerm(), None))


def _employee_inps(contract: Permanent | FixedTerm) -> Decimal:
    hired = date(2025, 1, 1)
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="telecomunicazioni-asstel",
                level_code="C1",
                contract_type=contract,
                employment_period=EmploymentPeriod(hired, None),
                seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), inps_sector=TaxSector.TERZIARIO
            ),
        )
    )
    (rate,) = (
        d.inputs["rate"] for d in result.decisions if d.capability == "inps_employee"
    )
    return Decimal(str(rate))


def test_a_fixed_term_loses_the_fis_share_and_pays_no_fund() -> None:
    """Terziario: 9.19% for the fixed term, 9.19% + 0.4167% for the permanent."""
    assert _employee_inps(FixedTerm()) == Decimal("0.0919")
    assert _employee_inps(Permanent()) == Decimal("0.0960666667")
