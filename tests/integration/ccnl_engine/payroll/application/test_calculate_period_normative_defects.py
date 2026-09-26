"""Normative P0 red tests — all marked xfail(strict=True).

Each test documents a correctness bug that causes the engine to produce
payslips that do not conform to Italian labour or tax law.  The expected
values are derived from primary sources (laws, INPS circulars) and are
independent of the engine implementation.

When a later PR fixes the underlying bug the xfail turns into an XPASS,
causing CI to fail and prompting the developer to remove the marker.

P0 findings:
  P0-01  BonusEvent used for PdR bonus — no substitute-tax regime
  P0-02  calculate_year always 12 periods — extra months ignored
  P0-03  taxable_ytd in PeriodState not used in IRPEF conguaglio
  P0-04  cross-period fringe retroactive adjustment missing
  P0-05  somma_esente computed but never posted to CREDITS ledger
  P0-06  1% INPS addizionale on income > 56,224 EUR not computed
  P0-07  lavoro-domestico-convivente.json raises TypeError
  P0-08  AbsenceEvent with impossible hours accepted silently

Sources:
  L. 199/2025 art. 1 co. 9: PdR substitute rate 1% up to 5,000 EUR
  INPS circ. 4/2026: 2026 IVS massimale 122,295 EUR; 1% threshold 56,224 EUR
  TUIR art. 51 co. 3-bis: fringe-benefit threshold; entire annual cumulated
    amount becomes taxable when threshold is crossed
  L. 160/2019 (as amended): somma_esente credit for reddito ≤ 28,000 EUR
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import ContributableHours, WeeklyHours
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    BonusEvent,
    FringeEvent,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import EarningsYtd, FringeYtd
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.helpers import year_input

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_ZERO = Decimal(0)


def _req(
    month: int = 1,
    opening: PeriodState | None = None,
    events: tuple[object, ...] = (),
    ccnl: str = _CCNL,
    level: str = _LEVEL,
    weekly_hours: int | None = None,
    contributable_hours: Decimal | None = None,
) -> PeriodCalculationRequest:
    if opening is None:
        opening = PeriodState.zero()
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=ccnl,
        level_code=level,
        opening_state=opening,
        events=events,  # type: ignore[arg-type]
        weekly_hours=None if weekly_hours is None else WeeklyHours(weekly_hours),
        contributable_hours=(
            None
            if contributable_hours is None
            else ContributableHours(contributable_hours)
        ),
    )


def _sum_account(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        _ZERO,
    )


# ---------------------------------------------------------------------------
# P0-01: BonusEvent posted as PdR bonus → substitute-tax applies
#
# L. 199/2025 art. 1 co. 9: PdR bonuses up to 5,000 EUR are subject to a
# 1% flat substitute tax in place of ordinary IRPEF.  A 1,000 EUR PdR bonus
# must produce SUBSTITUTE_TAX = 10.00 and MUST NOT increase ORDINARY_TAX.
# ---------------------------------------------------------------------------


def test_pdr_bonus_substitute_tax() -> None:
    """A 1,000 EUR PdR bonus must post SUBSTITUTE_TAX = 10.00.

    Source: L. 199/2025 art. 1 co. 9 — tassazione sostitutiva 1% on PdR up
    to 5,000 EUR.  Expected: SUBSTITUTE_TAX = Decimal("10.00").
    """
    bonus = BonusEvent(
        event_date=date(_YEAR, 1, 15),
        amount=Decimal("1000.00"),
        kind="productivity_bonus",
    )
    result = calculate_period(
        replace(
            _req(events=(bonus,)),
            prior_year=PriorYearTaxFacts(employment_income=Decimal("25000.00")),
        )
    )

    sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
    assert sub_tax == Decimal("10.00"), (
        f"SUBSTITUTE_TAX for a 1,000 EUR PdR bonus must be 10.00 (1% flat); "
        f"got {sub_tax}.  BonusEvent currently has no PdR classification."
    )


# ---------------------------------------------------------------------------
# P0-02: calculate_year always 12 periods — extra months ignored
#
# The calendar lists the extra months (tredicesima, quattordicesima), each
# paid in its own run.  calculate_year must produce one
# PeriodResult per payroll run, not always 12.
# Source: CCNL calendar, derived from additional_months.
# ---------------------------------------------------------------------------


def test_calculate_year_extra_months() -> None:
    """calculate_year with one extra month must produce 13 period results.

    Source: CCNL calendar (additional_months=13).  Expected: 13 periods.
    Fixed in feature/payroll-schedule: PayrollSchedule.from_calendar generates
    extra runs; calculate_year iterates schedule.runs instead of range(1, 13).
    """
    result = calculate_year(year_input(_YEAR, _CCNL, _LEVEL))
    assert len(result.period_results) == 13, (
        f"calculate_year with tredicesima must produce 13 period results; "
        f"got {len(result.period_results)}.  "
        "calculate_year.py:118 always loops range(1, 13)."
    )


# ---------------------------------------------------------------------------
# P0-03: taxable_ytd in PeriodState not used in IRPEF conguaglio
#
# The conguaglio (IRPEF settling) in the final period depends on the actual
# YTD taxable income, not only on the projected annual figure.  When
# taxable_ytd differs between two otherwise identical December requests the
# resulting IRPEF must differ.
# Source: TUIR art. 23 — ritenuta per conguaglio
# ---------------------------------------------------------------------------


def test_taxable_ytd_affects_conguaglio() -> None:
    """Different taxable_ytd must produce different IRPEF in the conguaglio.

    Source: TUIR art. 23.  Two December calculations, one with taxable_ytd=0
    and one with taxable_ytd=5,000, must produce different ordinary_tax.
    """
    opening_zero = PeriodState(
        ytd=TaxYearState(
            regular_periods_closed=11,
            tax_withholding_periods_closed=11,
        )
    )
    opening_high = PeriodState(
        ytd=TaxYearState(
            regular_periods_closed=11,
            tax_withholding_periods_closed=11,
            earnings=EarningsYtd(taxable=Decimal("5000.00")),
        )
    )
    result_zero = calculate_period(_req(month=12, opening=opening_zero))
    result_high = calculate_period(_req(month=12, opening=opening_high))

    tax_zero = result_zero.tax_computation.ordinary_tax
    tax_high = result_high.tax_computation.ordinary_tax
    assert tax_zero != tax_high, (
        "December IRPEF must differ when taxable_ytd differs: "
        f"taxable_ytd=0 -> {tax_zero}, "
        f"taxable_ytd=5000 -> {tax_high}.  "
        "taxable_ytd is ignored in the current projection (_compute_amounts.py)."
    )


# ---------------------------------------------------------------------------
# P0-04: cross-period fringe retroactive adjustment missing
#
# TUIR art. 51 co. 3-bis: when the annual cumulated fringe benefit exceeds
# the threshold, the ENTIRE annual cumulated amount is subject to INPS and
# IRPEF — including amounts that were previously exempt.  When fringe_ytd=600
# (exempt month 1) and a second FringeEvent(600) crosses the 1,000 EUR
# threshold in month 2, the engine must retroactively tax the prior 600 and
# report irpef_base = 1,200 for the combined period.
# ---------------------------------------------------------------------------


def test_fringe_retroactive_on_threshold_crossing() -> None:
    """irpef_base must cover the full cumulative fringe when crossing.

    Source: TUIR art. 51 co. 3-bis.  fringe_ytd=600 + FringeEvent(600) =
    1,200 > 1,000 threshold → irpef_base must equal 1,200 (full retroactive).
    """
    state_after_m1 = PeriodState(
        ytd=TaxYearState(
            regular_periods_closed=1,
            tax_withholding_periods_closed=1,
            fringe=FringeYtd(value=Decimal("600.00")),
        )
    )
    fringe = FringeEvent(event_date=date(_YEAR, 2, 15), amount=Decimal("600.00"))
    result = calculate_period(_req(month=2, opening=state_after_m1, events=(fringe,)))

    assert result.benefit_breakdown.irpef_base == Decimal("1200.00"), (
        "irpef_base after threshold crossing must be 1,200 (full cumulative "
        f"retroactive); got {result.benefit_breakdown.irpef_base}.  "
        "Currently only the current-period 600 is taxed."
    )


# ---------------------------------------------------------------------------
# P0-05: somma_esente computed but never posted to CREDITS ledger
#
# L. 160/2019 (art. 1 co. 3, as renamed): low-income workers whose reddito
# does not exceed 28,000 EUR receive a somma_esente credit that reduces IRPEF
# due.  The credit is computed inside compute_tax (visible in
# TaxComputation.components) but calculate_period never posts it to the
# CREDITS ledger account.
# Normative value for acconciatura-estetica level 3, month 6, 2026:
#   somma_esente = 834.11520 annual (computed but unposted)
#   expected CREDITS ≥ 1 EUR (any positive credit would satisfy the gate)
# ---------------------------------------------------------------------------


def test_somma_esente_posted_to_credits() -> None:
    """low-income worker must have CREDITS > 0 from somma_esente.

    Source: L. 160/2019 art. 1 co. 3.  Worker: acconciatura-estetica level 3,
    annual reddito ≈ 19,136 EUR < 28,000 EUR threshold.
    Expected: CREDITS > 0 in any period.
    """
    result = calculate_period(
        _req(month=6, ccnl="acconciatura-estetica-confartigianato.json", level="3")
    )
    tax_credits = _sum_account(result, AccountKind.CREDITS)
    assert tax_credits > _ZERO, (
        f"CREDITS for a low-income worker (acconciatura-estetica level 3) must "
        f"be > 0 due to the somma_esente credit (L. 160/2019); got {tax_credits}.  "
        "calculate_period posts only trattamento_integrativo to CREDITS and "
        "ignores the somma_esente component from TaxComputation."
    )


# ---------------------------------------------------------------------------
# P0-06: 1% INPS addizionale on income > 56,224 EUR not computed
#
# INPS circ. 4/2026: workers whose cumulated INPS contribution base exceeds
# 56,224 EUR pay an additional 1% on the excess (charged to the employee).
# The contribution breakdown must include an 'addizionale_1pct' component.
# Normative threshold 2026: 56,224 EUR (source: INPS circ. 4/2026).
# ---------------------------------------------------------------------------


def test_inps_addizionale_1pct_on_threshold_crossing() -> None:
    """1% addizionale must appear when INPS base crosses 56,224 EUR.

    Source: INPS circ. 4/2026.  With inps_base_ytd=56,000 and ~2,200 EUR
    monthly base the cumulative crosses 56,224 EUR; an 'addizionale_1pct'
    component with amount > 0 must appear in contribution_breakdown.
    """
    opening = PeriodState(
        ytd=TaxYearState(
            regular_periods_closed=5,
            tax_withholding_periods_closed=5,
            earnings=EarningsYtd(inps_base=Decimal("56000.00")),
        )
    )
    result = calculate_period(_req(month=6, opening=opening))

    component_names = {c.name for c in result.contribution_breakdown.components}
    assert "addizionale_1pct" in component_names, (
        "ContributionBreakdown must include 'addizionale_1pct' when the "
        "cumulative INPS base crosses 56,224 EUR (INPS circ. 4/2026).  "
        f"Current components: {sorted(component_names)}."
    )
    addizionale = next(
        (
            c.amount
            for c in result.contribution_breakdown.components
            if c.name == "addizionale_1pct"
        ),
        _ZERO,
    )
    assert addizionale > _ZERO, (
        f"'addizionale_1pct' amount must be > 0; got {addizionale}."
    )


# ---------------------------------------------------------------------------
# P0-07: lavoro-domestico-convivente.json raises TypeError
#
# calculate_period invokes resolve_rates which requires standard INPS rates.
# The domestic CCNL uses flat per-hour contributions and is incompatible with
# the standard rate path.  Any call with a domestic CCNL slug must not raise
# TypeError; it must return a valid PeriodResult.
# ---------------------------------------------------------------------------


def test_domestic_work_no_type_error() -> None:
    """calculate_period with a domestic CCNL returns a valid result.

    Source: CCNL lavoro domestico (CNEL A221).  Expected: valid result with
    period_gross > 0 and non-zero domestic INPS contributions.
    """
    req = _req(
        month=6,
        ccnl="lavoro-domestico-convivente.json",
        level="BS",
        weekly_hours=30,
        contributable_hours=Decimal(130),
    )
    result = calculate_period(req)
    assert result.period_gross > _ZERO, (
        "calculate_period for lavoro-domestico-convivente.json must return a "
        f"valid result with period_gross > 0; got {result.period_gross}."
    )
    assert result.contribution_breakdown.employee > _ZERO, (
        "Domestic CCNL must produce non-zero employee INPS contributions."
    )


# ---------------------------------------------------------------------------
# P0-08: AbsenceEvent with impossible hours accepted silently
#
# A monthly payroll period has at most ~184 working hours (23 days x 8 h).
# AbsenceEvent(hours=1000) in a single month is physically impossible and
# must raise InvalidInputError before reaching the computation.
# Currently the engine accepts it and produces a large negative period_gross.
# ---------------------------------------------------------------------------


def test_absence_event_impossible_hours_raises() -> None:
    """AbsenceEvent with 1,000 hours must raise InvalidInputError.

    Source: physical constraint — a month has at most ~184 working hours.
    Fixed in refactor/canonical-domain: _check_event_date validates hours <= 240.
    """
    absence = AbsenceEvent(
        event_date=date(_YEAR, 1, 15),
        hours=Decimal(1000),
        hourly_rate=Decimal("12.50"),
    )
    with pytest.raises(InvalidInputError):
        calculate_period(_req(events=(absence,)))
