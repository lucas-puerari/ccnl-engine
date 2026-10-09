"""Tax year attribution and obligations that survive the year change."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    Employment,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    UnsupportedTaxYearError,
)
from ccnl_engine.catalog import supported_tax_years
from ccnl_engine.inputs import (
    ContributableHours,
    InpsBaseYtd,
    NoPensionFund,
    OpeningBalances,
    PeriodState,
    Permanent,
    RecoveryObligation,
    RecoveryPlan,
    WeeklyHours,
)
from ccnl_engine.results import BlockerCode
from tests.acceptance.legal_scenarios._support import (
    COMMERCIO,
    EMPLOYER,
    ENGINE,
    regular_period,
)
from tests.fixtures.next_year_repository import NextYearRepository
from tests.fixtures.seniority import new_hire
from tests.fixtures.tfr import no_tfr_fund
from tests.fixtures.withholding import paid_before

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def test_december_paid_by_twelve_january_stays_in_previous_year() -> None:
    """Cassa allargata: pay paid by 12 January belongs to the previous year.

    Art. 51 c. 1 TUIR: December 2026 pay paid on 12 January 2027 is 2026 income.
    """
    result = regular_period(month=12, payment_date=date(2027, 1, 12))

    assert result.closing_state.tax_year == 2026


def test_december_paid_by_ten_january_stays_in_previous_year() -> None:
    """Art. 51 c. 1 TUIR: December 2026 paid on 10 January 2027 is 2026 income."""
    result = regular_period(month=12, payment_date=date(2027, 1, 10))

    assert result.closing_state.tax_year == 2026


def test_run_of_unbundled_tax_year_raises_domain_error() -> None:
    """The engine computes the run with the payment year's tables.

    No 2028 tables are bundled, so a run paid in 2028 fails with a domain
    error that names the attributed tax year instead of computing it with
    the rules of another year.
    """
    with pytest.raises(UnsupportedTaxYearError) as info:
        regular_period(month=12, payment_date=date(2028, 6, 28))

    assert info.value.year == 2028
    assert info.value.supported == supported_tax_years() == (2026, 2027)
    assert "2026, 2027" in (info.value.remediation or "")


def test_december_paid_in_january_reads_provisional_2027_tax_rules() -> None:
    """December 2026 paid on 13 January 2027: 2027 IRPEF, 2026 INPS.

    The payment belongs to tax year 2027 (art. 51 c. 1 TUIR), so the IRPEF
    rules are those of 2027; INPS follows competence (INPS circ. 237/2016
    par. 2.1).  The 2027 tables are provisional, carried over from 2026
    until the 2027 sources are published: the run is computed and not
    payable, with the open limitation ``provisional_ruleset``.
    """
    result = regular_period(month=12, payment_date=date(2027, 1, 13))
    rulesets = {r.id for r in result.assurance.rulesets}

    assert result.closing_state.tax_year == 2027
    assert {"tax/2027/terziario", "inps/2026/terziario"} <= rulesets
    assert "inps/2027/terziario" not in rulesets
    limitations = {lim.id for lim in result.assurance.limitations}
    assert "provisional_ruleset" in limitations
    assert "provisional_inps_ruleset" not in limitations
    assert (BlockerCode.OPEN_LIMITATION, "provisional_ruleset") in {
        (b.code, b.detail) for b in result.blockers
    }
    assert not result.is_payable


def test_domestic_run_of_2027_records_the_provisional_inps_rules() -> None:
    """A household employer withholds no IRPEF but pays 2027 INPS.

    January 2027 of a domestic worker reads the provisional 2027 INPS
    hourly contributions: the run records ``provisional_inps_ruleset``
    and is not payable, although the IRPEF limitation does not concern it.
    """
    employment = Employment(
        ccnl_slug="lavoro-domestico-non-convivente.json",
        level_code="A",
        seniority=new_hire(2027),
        tfr_fund=no_tfr_fund(2027),
        tfr_treasury_fund=False,
        contract_type=Permanent(),
        pension_fund=NoPensionFund(),
        weekly_hours=WeeklyHours(20),
    )
    result = regular_period(
        employment=employment,
        year=2027,
        month=1,
        contributable_hours=ContributableHours(Decimal(86)),
    )

    assert "inps/2027/lavoro-domestico" in {r.id for r in result.assurance.rulesets}
    assert (BlockerCode.OPEN_LIMITATION, "provisional_inps_ruleset") in {
        (b.code, b.detail) for b in result.blockers
    }
    assert not result.is_payable


def test_december_paid_in_december_reads_no_provisional_rules() -> None:
    """December 2026 paid in 2026 reads only the 2026 tables."""
    result = regular_period(month=12, payment_date=date(2026, 12, 27))

    assert "provisional_ruleset" not in {lim.id for lim in result.assurance.limitations}


def test_run_of_next_tax_year_is_not_added_to_current_year_state() -> None:
    """December 2026 paid on 13 January 2027 cannot close into the 2026 state."""
    ytd = replace(
        PeriodState.zero().cash,
        tax_year=2026,
    )
    opening = PeriodState(cash=ytd)

    with pytest.raises(InvalidInputError, match="belongs to tax year 2027"):
        regular_period(month=12, payment_date=date(2027, 1, 13), opening_state=opening)


_PLAN = RecoveryPlan(
    kind="trattamento_integrativo",
    original_amount=Decimal(160),
    installment_amount=Decimal(20),
    installments_total=8,
    installments_posted=2,
)
_NEXT_YEAR_ENGINE = PayrollEngine(repository=NextYearRepository())


def _december_2026() -> tuple[PeriodResult, PeriodResult]:
    """Close 2026 on Commercio L4: December, then the tredicesima.

    The opening balances come from a previous provider: 11 regular runs and
    the quattordicesima paid, 160.00 of trattamento integrativo recognized
    and a recovery plan of 8 x 20.00 with 2 installments posted (40.00).

    Returns:
        The December and tredicesima results, in payment order.
    """
    opening = PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            payments=paid_before(PayrollRun.regular(2026, 12), 14),
            trattamento_recognized=Decimal(160),
            trattamento_recovered=Decimal(40),
            recoveries=(RecoveryObligation(tax_year=2026, plan=_PLAN),),
            inps_bases=(InpsBaseYtd(2026, other_employers=Decimal(0)),),
            surtax_obligations=(),
        )
    )
    december = regular_period(month=12, opening_state=opening)
    thirteenth = ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12),
            payment_date=date(2026, 12, 27),
            employment=Employment(
                ccnl_slug=COMMERCIO, level_code="4", contract_type=Permanent()
            ),
            employer=EMPLOYER,
            opening_state=december.closing_state,
        )
    )
    return december, thirteenth


def _january_2027(opening: PeriodState) -> PeriodResult:
    """Compute January 2027 on 2026 rules standing in for 2027.

    Returns:
        The January 2027 result.
    """
    return _NEXT_YEAR_ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2027, 1),
            payment_date=date(2027, 1, 27),
            employment=Employment(
                ccnl_slug=COMMERCIO, level_code="4", contract_type=Permanent()
            ),
            employer=EMPLOYER,
            opening_state=opening,
        )
    )


def _without_obligations(state: PeriodState) -> object:
    """Return the tax cash state of ``state`` with no obligation carried.

    Returns:
        ``state.cash`` with the obligations of a new employment.
    """
    return replace(state.cash, obligations=PeriodState.zero().cash.obligations)


def test_installment_recovery_survives_the_year_change() -> None:
    """D.L. 3/2020 art. 1 c. 3: recovery above 60 EUR runs in 8 installments.

    A plan of 160.00 EUR in 8 installments of 20.00 with 2 posted before
    December posts the third in December and the fourth on the tredicesima,
    leaving 4 installments (80.00) for 2027.  The state that opens 2027 has
    fresh year-to-date accounts and still carries them.
    """
    _, thirteenth = _december_2026()

    next_year = ENGINE.close_tax_year(thirteenth.closing_state)

    (carried,) = next_year.cash.obligations.recoveries
    assert carried.tax_year == 2026
    assert carried.plan.installments_posted == 4
    assert carried.plan.residual == Decimal("80.00")
    assert _without_obligations(next_year) == replace(
        PeriodState.zero().cash, tax_year=2027
    )
    assert next_year.accrual == thirteenth.closing_state.accrual


def test_close_tax_year_rejects_a_state_before_the_last_run() -> None:
    """The tredicesima is still due: 2026 cannot be closed after December."""
    december, _ = _december_2026()

    with pytest.raises(InvalidInputError, match="did not settle the conguaglio"):
        ENGINE.close_tax_year(december.closing_state)


def test_carried_installment_is_deducted_in_the_next_year() -> None:
    """January 2027 deducts the fifth installment and keeps its own credit.

    Differential oracle on the same 2027 run with and without the carried
    plan: net pay is exactly 20.00 lower, the plan moves from 4 to 5 posted
    (residual 60.00), and the 2027 trattamento integrativo account is the
    same as without the plan, because a 2026 recovery is not a 2027 credit.
    """
    _, thirteenth = _december_2026()
    opening = ENGINE.close_tax_year(thirteenth.closing_state)

    with_plan = _january_2027(opening)
    without_plan = _january_2027(
        replace(
            opening,
            cash=replace(opening.cash, obligations=PeriodState.zero().cash.obligations),
        )
    )

    assert without_plan.period_net - with_plan.period_net == Decimal("20.00")
    (carried,) = with_plan.closing_state.cash.obligations.recoveries
    assert carried.plan.installments_posted == 5
    assert carried.plan.residual == Decimal("60.00")
    assert _without_obligations(with_plan.closing_state) == _without_obligations(
        without_plan.closing_state
    )
    recovery = [
        item
        for item in with_plan.pay_items
        if item.item_id == "trattamento_integrativo_recovery_2026_2027-01-regular"
    ]
    assert [item.amount for item in recovery] == [Decimal(-20)]
    (decision,) = [
        d
        for d in with_plan.decisions
        if d.capability == "trattamento_integrativo_recovery"
    ]
    assert decision.reason_code == "installment_posted"
    assert decision.amount == Decimal(-20)
    assert decision.inputs["origin_tax_year"] == "2026"
    assert decision.inputs["installment_number"] == Decimal(5)
