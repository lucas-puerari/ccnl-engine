"""Withholding invariants of period runs.

The annual IRPEF reconciles and a large bonus is withheld on the payslip
that pays it.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_competence_year import (
    calculate_competence_year,
)
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.invariants._types import RunFacts
from ccnl_engine.payroll.application.invariants.withholding import (
    check_irpef_annual_reconciliation,
    net_annual_irpef,
)
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.events import BonusEvent
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.domain.tax import TaxComputation, TaxLineItem
from ccnl_engine.payroll.domain.ytd_accounts import WithholdingShortfall
from tests.fixtures.normative_oracles.irpef_2026 import net_irpef as oracle_net_irpef
from tests.helpers import year_plan

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.year_result import CompetenceYearResult
    from ccnl_engine.payroll.domain.period import PeriodResult

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_OPENING = PeriodState.zero()
_CEILING = Decimal(122_295)


def _run(
    month: int = 1,
    opening: PeriodState = _OPENING,
    **kwargs: object,
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=_YEAR, month=month),
            payment_date=date(_YEAR, month, 27),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            employer=EmployerProfile(headcount=Headcount(50)),
            opening_state=opening,
            **kwargs,  # type: ignore[arg-type]
        )
    )


def _with_ytd(result: PeriodResult, **ytd: object) -> PeriodResult:
    state = result.closing_state
    closing = replace(state, cash=replace(state.cash, **ytd))  # type: ignore[arg-type]
    return replace(result, closing_state=closing)


@cache
def _last_two() -> tuple[PeriodResult, PeriodResult]:
    results = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL)).period_results
    return results[-2], results[-1]


class TestIrpefAnnualReconciliation:
    """The run closing the last withholding slot settles the IRPEF of the year."""

    def test_real_year_passes(self) -> None:
        """The conguaglio of a real year settles the net annual IRPEF."""
        previous, last = _last_two()
        assert last.closing_state.cash.is_complete
        assert (
            check_irpef_annual_reconciliation(last, previous.closing_state, RunFacts())
            == []
        )

    def test_withheld_off_by_more_than_a_cent_is_reported(self) -> None:
        """IRPEF withheld one euro above the annual IRPEF is a violation."""
        previous, last = _last_two()
        tax = last.closing_state.cash.tax
        bad = _with_ytd(last, tax=replace(tax, irpef=tax.irpef + 1))

        (violation,) = check_irpef_annual_reconciliation(
            bad, previous.closing_state, RunFacts()
        )
        assert violation.invariant_id == "irpef_annual_reconciliation"
        assert violation.actual == violation.expected + 1  # type: ignore[operator]

    def test_shortfall_left_counts_as_due(self) -> None:
        """IRPEF the pay did not cover still settles the year with it."""
        previous, last = _last_two()
        tax = last.closing_state.cash.tax
        short = _with_ytd(
            last,
            tax=replace(tax, irpef=tax.irpef - 30),
            shortfall=WithholdingShortfall(irpef=Decimal(30)),
        )
        assert (
            check_irpef_annual_reconciliation(short, previous.closing_state, RunFacts())
            == []
        )

    def test_one_cent_is_within_rounding(self) -> None:
        """A one-cent difference is rounding, not a violation."""
        previous, last = _last_two()
        tax = last.closing_state.cash.tax
        bad = _with_ytd(last, tax=replace(tax, irpef=tax.irpef + Decimal("0.01")))
        assert (
            check_irpef_annual_reconciliation(bad, previous.closing_state, RunFacts())
            == []
        )

    def test_earlier_slot_is_not_checked(self) -> None:
        """A run before the last slot is not reconciled."""
        result = _run()
        tax = result.closing_state.cash.tax
        bad = _with_ytd(result, tax=replace(tax, irpef=tax.irpef + 1))
        assert check_irpef_annual_reconciliation(bad, _OPENING, RunFacts()) == []

    def test_projected_taxable_off_final_is_reported(self) -> None:
        """IRPEF settled on a taxable other than the final one is a violation."""
        previous, last = _last_two()
        final = last.closing_state.cash.earnings.taxable
        facts = RunFacts(projected_taxable=final + Decimal("22.11"))

        (violation,) = check_irpef_annual_reconciliation(
            last, previous.closing_state, facts
        )
        assert violation.invariant_id == "irpef_annual_reconciliation"
        assert violation.expected == final
        assert violation.actual == final + Decimal("22.11")

    def test_two_cents_of_taxable_are_rounding(self) -> None:
        """A two-cent taxable difference is rounding, not a violation."""
        previous, last = _last_two()
        final = last.closing_state.cash.earnings.taxable
        facts = RunFacts(projected_taxable=final - Decimal("0.02"))
        assert (
            check_irpef_annual_reconciliation(last, previous.closing_state, facts) == []
        )

    def test_high_earner_settles_on_final_taxable(self) -> None:
        """Above the 1% addizionale threshold the last slot uses actual INPS.

        Bancari QD4 earns about 67,000 EUR, above the 56,224 EUR threshold
        of the 1% addizionale INPS (INPS circ. 6/2026 par. 5).  The last run must
        project its taxable income with the INPS it actually withholds, so
        the conguaglio settles the IRPEF of the final taxable income.
        """
        results = calculate_competence_year(
            year_plan(_YEAR, "bancari-abi.json", "QD4")
        ).period_results
        last = results[-1]
        assert last.closing_state.cash.tax.irpef == net_annual_irpef(
            last.tax_computation
        )

    def test_net_annual_irpef_uses_deductions_only(self) -> None:
        """Credits paid on the payslip do not lower the IRPEF due."""
        computation = TaxComputation(
            ordinary_tax=Decimal(0),
            trattamento_integrativo=Decimal(0),
            withholding_due=Decimal(0),
            components=(
                TaxLineItem("irpef_gross", Decimal(1_000), "art11-tuir", "Art. 11"),
                TaxLineItem("work_deduction", Decimal(300), "art13-tuir", "Art. 13"),
                TaxLineItem(
                    "trattamento_integrativo", Decimal(1_200), "dl3", "D.L. 3/2020"
                ),
            ),
        )
        assert net_annual_irpef(computation) == Decimal(700)

    def test_net_annual_irpef_is_floored_at_zero(self) -> None:
        """Deductions above the gross IRPEF give no IRPEF due."""
        computation = TaxComputation(
            ordinary_tax=Decimal(0),
            trattamento_integrativo=Decimal(0),
            withholding_due=Decimal(0),
            components=(
                TaxLineItem("irpef_gross", Decimal(100), "art11-tuir", "Art. 11"),
                TaxLineItem("work_deduction", Decimal(300), "art13-tuir", "Art. 13"),
            ),
        )
        assert net_annual_irpef(computation) == Decimal(0)


def _november_irpef(result: CompetenceYearResult) -> Decimal:
    (november,) = (
        r
        for r in result.period_results
        if r.period_id.month == 11
        and r.run is not None
        and r.run.run_kind is RunKind.REGULAR
    )
    return november.tax_computation.ordinary_tax


def _final_taxable(result: CompetenceYearResult) -> Decimal:
    return result.period_results[-1].closing_state.cash.earnings.taxable


def test_large_bonus_leaves_every_net_non_negative() -> None:
    """A 20,000 EUR bonus in November must not make a later net negative.

    The IRPEF of the bonus used to be withheld over the remaining slots of
    the year instead of on the bonus payslip, so the tredicesima run
    withheld more than it paid and ``net_pay_non_negative`` rejected the
    year.
    """
    bonus = BonusEvent(event_date=date(_YEAR, 11, 10), amount=Decimal(20_000))
    result = calculate_competence_year(
        year_plan(_YEAR, _CCNL, _LEVEL, events={11: (bonus,)})
    )
    assert all(r.period_net >= 0 for r in result.period_results)


def test_large_bonus_is_withheld_on_the_payslip_that_pays_it() -> None:
    """A 20,000 EUR bonus in November is taxed on the November payslip.

    Art. 23 c. 2 lett. a) DPR 600/1973 withholds on the sums paid in each
    pay period.  The November run withholds its share of the recurring tax
    plus the whole tax the bonus adds to the year; spreading that tax over
    the later slots made the tredicesima run withhold more than it paid.

    November also charges the additional 1% IVS on its pay above 4,685.00
    (INPS circ. 6/2026 par. 5): 2,211.43 + 20,000 - 4,685 = 17,526.43,
    x 1% = 175.2643 -> 175.26, deducted from its taxable income
    (art. 51 c. 2 lett. a TUIR).  The pay of the year stays below 56,224,
    so the December conguaglio gives the 175.26 back and the later runs
    withhold the tax on it (msg. INPS 5327/2015 par. 2.3).

    Expected, from the oracle on the final taxable incomes of the year with
    and without the bonus: the November IRPEF grows by
    ``net_irpef(with - 175.26) - net_irpef(without)``, and the runs after it
    withhold ``net_irpef(with) - net_irpef(with - 175.26)`` more than
    without the bonus.  The tolerance of 0.50 EUR is the rounding of the
    projection of the later slots, which the conguaglio settles.
    """
    bonus = BonusEvent(event_date=date(_YEAR, 11, 10), amount=Decimal(20_000))
    with_bonus = calculate_competence_year(
        year_plan(_YEAR, _CCNL, _LEVEL, events={11: (bonus,)})
    )
    without = calculate_competence_year(year_plan(_YEAR, _CCNL, _LEVEL))
    november_additional_ivs = Decimal("175.26")

    final_with = _final_taxable(with_bonus)
    bonus_tax = oracle_net_irpef(final_with - november_additional_ivs) - (
        oracle_net_irpef(_final_taxable(without))
    )
    refund_tax = oracle_net_irpef(final_with) - oracle_net_irpef(
        final_with - november_additional_ivs
    )
    grown = _november_irpef(with_bonus) - _november_irpef(without)

    tail_growth = sum(
        (
            a.tax_computation.ordinary_tax - b.tax_computation.ordinary_tax
            for a, b in zip(
                with_bonus.period_results[-2:], without.period_results[-2:], strict=True
            )
        ),
        Decimal(0),
    )

    assert abs(grown - bonus_tax) <= Decimal("0.50")
    assert abs(tail_growth - refund_tax) <= Decimal("0.50")
