"""Construction Art. 65: a monthly award at each qualifying hire anniversary.

With EUR 2,000 monthly chain pay and one award month, the award is EUR 2,000;
INPS, TFR and IRPEF bases each increase by EUR 2,000, not extra-month pay.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.compensation.loyalty.rules import loyalty_premium
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.total.handlers import _EventTotals
from ccnl_engine.pay_item.policies import PolicyContext
from ccnl_engine.pay_item.selection.policies import CompetencePeriod
from ccnl_engine.period.context.services import RunContext
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource


def _context(
    month: int = 4,
    start: date | None = date(2006, 4, 15),
    *,
    kind: RunKind = RunKind.REGULAR,
    service_start: date | None = None,
    agreement: str = "edilizia-artigianato-cna",
    year: int = 2026,
) -> RunContext:
    return cast(
        "RunContext",
        SimpleNamespace(
            contract=SimpleNamespace(
                ccnl=SimpleNamespace(
                    ruleset=None,
                    meta=SimpleNamespace(ccnl_id=agreement),
                    parameters=SimpleNamespace(
                        loyalty_premium=SimpleNamespace(
                            service_years=20,
                            months=Decimal(1),
                            provenance=SimpleNamespace(
                                location=SimpleNamespace(section="Art. 65")
                            ),
                        )
                    ),
                ),
                tctx=SimpleNamespace(payment=date(year, month, 27)),
            ),
            request=SimpleNamespace(
                employment_period=(
                    None
                    if start is None
                    else EmploymentPeriod(
                        started_on=start,
                        uninterrupted_service_started_on=service_start,
                    )
                ),
                period_id=SimpleNamespace(year=year, month=month),
            ),
            worker_category=WorkerCategory.IMPIEGATO,
            run_kind=kind,
            regular_chain=SimpleNamespace(
                base=Decimal(1800), seniority=Decimal(200), allowances=()
            ),
            resolver=bundled_policies(),
            policy_context=PolicyContext(year=year, as_of=date(year, month, 27)),
            run_id=f"{year}_{month:02d}_regular",
            cp=CompetencePeriod(year=year, month=month),
        ),
    )


def test_twentieth_anniversary_posts_earning_and_all_three_bases() -> None:
    """EUR 1,800 base + EUR 200 seniority = EUR 2,000 in each base."""
    paid = loyalty_premium(_context())
    assert paid.amount == Decimal(2000)
    assert paid.items[0].kind == "loyalty_premium_earning"
    assert paid.entries[0].amount == Decimal(2000)
    assert paid.entries[0].policy_decision_id is not None
    assert paid.taxed == (True, True, True)
    assert paid.decisions[0].reason_code == "loyalty_anniversary"
    totals = _EventTotals(
        inps_base=Decimal(0),
        tfr_base=Decimal(0),
        irpef_base=Decimal(0),
        fringe_value=Decimal(0),
        fringe_inps=Decimal(0),
        fringe_irpef=Decimal(0),
        substitute_base=Decimal(0),
    )
    updated = paid.added_to(totals)
    assert (updated.inps_base, updated.tfr_base, updated.irpef_base) == (
        Decimal(2000),
        Decimal(2000),
        Decimal(2000),
    )


@pytest.mark.parametrize(
    ("month", "start", "kind"),
    [
        (5, date(2006, 4, 15), RunKind.REGULAR),
        (4, date(2007, 4, 15), RunKind.REGULAR),
        (4, None, RunKind.REGULAR),
        (4, date(2006, 4, 15), RunKind.THIRTEENTH),
    ],
)
def test_no_award_outside_qualifying_regular_anniversary(
    month: int, start: date | None, kind: RunKind
) -> None:
    """EUR 2,000 chain pay produces EUR 0 absent a qualifying anniversary."""
    paid = loyalty_premium(_context(month, start, kind=kind))
    assert paid.amount == 0
    assert not paid.items
    assert not paid.entries


@pytest.mark.parametrize(
    "agreement", ["edilizia-artigianato-cna", "edilizia-pmi-confapi-aniem"]
)
def test_actual_uninterrupted_service_controls_award_month(agreement: str) -> None:
    """EUR 1,800 + EUR 200 = EUR 2,000 in April 2026 with no excluded service.

    With a 2007 actual-service start the same hire
    anniversary pays EUR 0 in 2026, and EUR 2,000 in April 2027.
    """
    without = _context(agreement=agreement)
    excluded = _context(service_start=date(2007, 4, 15), agreement=agreement)
    vested = _context(
        start=date(2005, 4, 15),
        service_start=date(2006, 4, 15),
        agreement=agreement,
    )
    assert loyalty_premium(without).amount == Decimal(2000)
    assert loyalty_premium(excluded).amount == Decimal(0)
    assert loyalty_premium(
        _context(service_start=date(2007, 4, 15), agreement=agreement, year=2027)
    ).amount == Decimal(2000)
    assert loyalty_premium(vested).amount == Decimal(2000)


def test_group_service_before_hire_preserves_hire_anniversary() -> None:
    """A 2010 hire with group service since 2006 gets EUR 2,000 in April.

    The April 2026 award is EUR 2,000, not EUR 0; March pays EUR 0.
    """
    april = _context(
        start=date(2010, 4, 15),
        service_start=date(2006, 4, 15),
        agreement="edilizia-pmi-confapi-aniem",
    )
    march = _context(
        3,
        start=date(2010, 4, 15),
        service_start=date(2006, 4, 15),
        agreement="edilizia-pmi-confapi-aniem",
    )
    assert loyalty_premium(april).amount == Decimal(2000)
    assert loyalty_premium(march).amount == 0


def test_service_start_after_hire_anniversary_waits_for_next_year() -> None:
    """Twenty years complete on April 30: April 15 pays EUR 0, not EUR 2,000."""
    assert loyalty_premium(_context(service_start=date(2006, 4, 30))).amount == 0


def test_actual_service_cannot_start_after_employment_ends() -> None:
    """An impossible service start is rejected rather than paying EUR 2,000."""
    with pytest.raises(InvalidInputError, match="uninterrupted service cannot start"):
        EmploymentPeriod(
            started_on=date(2006, 4, 15),
            ended_on=date(2026, 4, 14),
            uninterrupted_service_started_on=date(2026, 4, 15),
        )


def test_later_anniversary_still_pays() -> None:
    """At 21 completed years, the EUR 2,000 award recurs."""
    assert loyalty_premium(_context(start=date(2005, 4, 15))).amount == 2000


def test_cna_agreement_anniversary_is_posted_only_for_clerical_worker() -> None:
    """A 20-year hire anniversary pays one run-chain monthly award, not zero."""

    def run(month: int) -> PeriodResult:
        return calculate_period(
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(20)),
                period_id=PeriodId(2026, month),
                payment_date=date(2026, month, 27),
                ccnl_id="edilizia-artigianato-cna",
                level_code="7",
                opening_state=PeriodState.zero(),
                roles=frozenset(),
                events=(),
                employment_period=EmploymentPeriod(started_on=date(2006, 4, 15)),
            ),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )

    april = run(4)
    may = run(5)
    award = [i for i in april.pay_items if i.kind == "loyalty_premium_earning"]
    assert len(award) == 1
    assert award[0].amount > 0
    assert not [i for i in may.pay_items if i.kind == "loyalty_premium_earning"]


def test_ance_impiegato_twentieth_anniversary_amount_and_timing() -> None:
    """The 20-year award is EUR 2,143.99; the preceding month pays zero.

    EUR 1,564.31 minimum + 521.25 cost-of-living + 10.33 EDR
    + 5 x 9.62 seniority increments = EUR 2,143.99.
    This is the run-chain approximation of Art. 44 items 1-15; the provincial
    and individual elements are absent. The preceding month pays EUR 0.
    """

    def run(month: int) -> PeriodResult:
        return calculate_period(
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(20)),
                period_id=PeriodId(2026, month),
                payment_date=date(2026, month, 27),
                ccnl_id="edilizia-ance-impiegati",
                level_code="4",
                opening_state=PeriodState.zero(),
                roles=frozenset(),
                events=(),
                employment_period=EmploymentPeriod(started_on=date(2006, 4, 15)),
                seniority=SeniorityFact(239, date(2026, 3, 1), SenioritySource.PAYSLIP),
            ),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )

    april = run(4)
    march = run(3)
    award = [i for i in april.pay_items if i.kind == "loyalty_premium_earning"]
    assert len(award) == 1
    assert award[0].amount == Decimal("2143.99")
    assert not [i for i in march.pay_items if i.kind == "loyalty_premium_earning"]
