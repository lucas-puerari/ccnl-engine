"""Fringe benefit threshold and taxable amount, through the public API.

Rule (2026): L. 207/2024 art. 1 c. 390, in derogation of TUIR art. 51 c. 3,
exempts goods and services granted to an employee "entro il limite
complessivo di 1.000 euro" per tax year for 2025, 2026 and 2027, raised to
2.000 euro for a worker with children "che si trovano nelle condizioni
previste dall'articolo 12, comma 2" TUIR, the own-income limit (2.840,51
euro, 4.000 euro up to 24 years of age), who declares them to the employer
(c. 391): the children of the family composition.  AdE circolare 4/E of 16 May 2025,
par. 2.7: exceeding the limit "comporta la concorrenza dell'intero
ammontare, e non soltanto della quota parte eccedente".  The engine puts
the same taxable value in the INPS base, as it did before (art. 12 L.
153/1969 aligns the contribution base to art. 51 TUIR); that alignment is
existing behaviour, not re-verified by these tests.

Every expected value below follows from that rule by hand: the year total
is compared with the threshold; within it nothing is taxable, above it the
part of the year total not yet taxed becomes taxable in the run.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.events import FringeEvent
from ccnl_engine.inputs import (
    DependentRelationship,
    FamilyComposition,
    PeriodState,
    Permanent,
)
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.period._capability_traces import build_traces
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import FringeBenefitItem
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import FringeYtd
from tests.fixtures.dependents import declared_dependent
from tests.fixtures.period_requests import account_total, period_request

engine = PayrollEngine.bundled()

_D = Decimal
_YEAR = 2026
_STANDARD = _D(1000)
_WITH_CHILDREN = _D(2000)


_CHILD = declared_dependent(DependentRelationship.CHILD, birth_date=date(2015, 1, 1))
_NO_FAMILY = FamilyComposition()


def _run(
    month: int,
    *amounts: Decimal,
    children: bool = False,
    family: FamilyComposition | None = _NO_FAMILY,
    opening: PeriodState | None = None,
) -> PeriodResult:
    """Return the run with fringe benefits ``amounts``.

    ``children`` replaces ``family`` with one child within the own-income
    limit of art. 12 c. 2 TUIR.

    Returns:
        The run of ``month``.
    """
    if children:
        family = FamilyComposition(dependents=(_CHILD,))
    events = tuple(
        FringeEvent(event_date=date(_YEAR, month, 1), amount=a) for a in amounts
    )
    return engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=_YEAR, month=month),
            payment_date=date(_YEAR, month, 27),
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(100)),
            facts=PeriodFacts(events=events, family_composition=family),
            opening_state=opening or PeriodState.zero(),
        )
    )


def _item(result: PeriodResult, index: int = 0) -> FringeBenefitItem:
    items = [i for i in result.pay_items if isinstance(i, FringeBenefitItem)]
    return items[index]


def _decisions(result: PeriodResult) -> list[CalculationDecision]:
    return [d for d in result.decisions if d.capability == "fringe_benefit"]


class TestSingleRun:
    """One fringe benefit in one run, no earlier fringe in the year."""

    def test_above_threshold_whole_amount_taxable(self) -> None:
        """1.400 > 1.000: the whole 1.400 is taxable, not the 400 excess."""
        result = _run(3, _D(1400))
        item = _item(result)
        assert item.threshold_annual == _STANDARD
        assert item.ytd_total == _D(1400)
        assert item.taxable_amount == _D(1400)
        (decision,) = _decisions(result)
        assert decision.status is CalculationStatus.FINAL
        assert decision.reason_code == "above_threshold"
        assert decision.amount == _D(1400)
        assert decision.inputs["threshold_annual"] == _STANDARD
        assert decision.inputs["dependent_children"] == "false"
        assert decision.inputs["ytd_total"] == _D(1400)
        assert decision.inputs["retroactive_amount"] == _D(0)
        assert decision.rule == "tax/variable-pay-rules/2026"
        assert decision.source is not None
        assert decision.source.section == "art. 1 cc. 390-391"
        assert result.benefit_breakdown.irpef_base == _D(1400)

    def test_taxable_amount_enters_inps_base(self) -> None:
        """The INPS base of the run grows by the 1.400 taxable amount."""
        base = _run(3)
        result = _run(3, _D(1400))
        grown = (
            result.closing_state.accrual.inps_base(2026).own
            - base.closing_state.accrual.inps_base(2026).own
        )
        assert grown == _D(1400)

    def test_below_threshold_exempt_with_threshold_reported(self) -> None:
        """400 <= 1.000: exempt, and the item still reports the threshold."""
        base = _run(3)
        result = _run(3, _D(400))
        item = _item(result)
        assert item.threshold_annual == _STANDARD
        assert item.ytd_total == _D(400)
        assert item.taxable_amount == _D(0)
        (decision,) = _decisions(result)
        assert decision.reason_code == "within_threshold"
        assert decision.amount == _D(0)
        assert result.period_net == base.period_net

    def test_exactly_at_threshold_is_exempt(self) -> None:
        """1.000 is "entro il limite": exempt, the limit is not exceeded."""
        result = _run(3, _D(1000))
        assert _item(result).taxable_amount == _D(0)
        assert _decisions(result)[0].reason_code == "within_threshold"

    def test_one_trace_per_fringe_capability(self) -> None:
        """The event trace and the decision give a single fringe trace."""
        result = _run(3, _D(1400))
        traces = build_traces(result.decisions, frozenset({"fringe_benefit"}))
        assert [t.feature for t in traces].count("fringe_benefit") == 1


class TestCrossingInLaterRun:
    """A later run crosses the threshold: earlier exempt amounts are taxed."""

    def test_earlier_amounts_become_taxable(self) -> None:
        """600 in February (exempt), 600 in March: 1.200 taxable in March."""
        february = _run(2, _D(600))
        assert _item(february).taxable_amount == _D(0)
        march = _run(3, _D(600), opening=february.closing_state)
        item = _item(march)
        assert item.ytd_total == _D(1200)
        assert item.taxable_amount == _D(1200)
        (decision,) = _decisions(march)
        assert decision.reason_code == "above_threshold_retroactive"
        assert decision.inputs["ytd_before"] == _D(600)
        assert decision.inputs["retroactive_amount"] == _D(600)
        assert march.benefit_breakdown.irpef_base == _D(1200)
        assert march.closing_state.cash.fringe.value == _D(1200)
        assert march.closing_state.cash.fringe.taxed == _D(1200)

    def test_after_crossing_only_new_amount_taxable(self) -> None:
        """April 300 after 1.200 already taxed: only the 300 is taxable."""
        february = _run(2, _D(600))
        march = _run(3, _D(600), opening=february.closing_state)
        april = _run(4, _D(300), opening=march.closing_state)
        assert _item(april).ytd_total == _D(1500)
        assert _item(april).taxable_amount == _D(300)
        (decision,) = _decisions(april)
        assert decision.reason_code == "above_threshold"
        assert decision.inputs["taxed_before"] == _D(1200)

    def test_two_events_in_one_run_cross_on_the_second(self) -> None:
        """600 + 600 in one run: the second event taxes both, 1.200."""
        result = _run(3, _D(600), _D(600))
        assert _item(result, 0).taxable_amount == _D(0)
        assert _item(result, 1).taxable_amount == _D(1200)
        reasons = [d.reason_code for d in _decisions(result)]
        assert reasons == ["within_threshold", "above_threshold_retroactive"]


class TestDependentChildren:
    """A declared dependent child raises the threshold to 2.000."""

    def test_same_amount_exempt_only_with_children(self) -> None:
        """1.500: taxable against 1.000, exempt against 2.000."""
        without = _run(3, _D(1500))
        with_children = _run(3, _D(1500), children=True)
        assert _item(without).taxable_amount == _D(1500)
        item = _item(with_children)
        assert item.threshold_annual == _WITH_CHILDREN
        assert item.taxable_amount == _D(0)
        (decision,) = _decisions(with_children)
        assert decision.inputs["dependent_children"] == "true"
        assert decision.inputs["threshold_annual"] == _WITH_CHILDREN

    def test_crossing_the_higher_threshold(self) -> None:
        """1.500 in February, 600 in March: 2.100 > 2.000, all taxable."""
        february = _run(2, _D(1500), children=True)
        march = _run(3, _D(600), children=True, opening=february.closing_state)
        item = _item(march)
        assert item.ytd_total == _D(2100)
        assert item.taxable_amount == _D(2100)
        assert _decisions(march)[0].inputs["retroactive_amount"] == _D(1500)

    def test_child_of_24_within_the_higher_income_limit(self) -> None:
        """A child turning 24 in 2026 with 3.500 of own income counts.

        Art. 12 c. 2: the limit is 4.000 for a child "di età non superiore
        a ventiquattro anni"; 3.500 <= 4.000.  The age band of lett. c does
        not matter: c. 390 refers to c. 2 alone.
        """
        child = replace(_CHILD, birth_date=date(2002, 6, 1), own_income=_D(3500))
        result = _run(3, _D(1500), family=FamilyComposition(dependents=(child,)))
        assert _item(result).threshold_annual == _WITH_CHILDREN

    def test_child_above_the_income_limit_does_not_count(self) -> None:
        """A child of 11 with 4.000,01 of own income is not within c. 2."""
        child = replace(_CHILD, own_income=_D("4000.01"))
        result = _run(3, _D(1500), family=FamilyComposition(dependents=(child,)))
        assert _item(result).threshold_annual == _STANDARD
        assert _decisions(result)[0].inputs["dependent_children"] == "false"

    def test_child_dependent_only_in_another_year_does_not_count(self) -> None:
        """A dependency that ended in 2025 does not touch the 2026 year."""
        child = replace(_CHILD, dependent_until=date(2025, 12, 31))
        result = _run(3, _D(1500), family=FamilyComposition(dependents=(child,)))
        assert _item(result).threshold_annual == _STANDARD

    def test_ascendant_is_not_a_child(self) -> None:
        """Only children select the higher threshold."""
        parent = declared_dependent(DependentRelationship.ASCENDANT)
        result = _run(3, _D(1500), family=FamilyComposition(dependents=(parent,)))
        assert _item(result).threshold_annual == _STANDARD


class TestUnknownChildren:
    """An unknown children condition never selects a threshold silently."""

    def test_unknown_own_income_of_a_child_blocks_when_it_matters(self) -> None:
        """1.500 is taxable against 1.000 and exempt against 2.000.

        The standard threshold is applied, the decision is provisional and
        the run names the missing own income.
        """
        child = replace(_CHILD, own_income=None)
        result = _run(3, _D(1500), family=FamilyComposition(dependents=(child,)))
        assert _item(result).taxable_amount == _D(1500)
        (decision,) = _decisions(result)
        assert decision.status is CalculationStatus.PROVISIONAL
        assert decision.inputs["dependent_children"] == "unknown"
        (issue,) = [
            i for i in result.issues if i.code == "fringe_threshold_undetermined"
        ]
        assert issue.fact == "own_income"

    def test_unknown_family_blocks_when_it_matters(self) -> None:
        """Without a family composition the threshold is unknown."""
        result = _run(3, _D(1500), family=None)
        (issue,) = [
            i for i in result.issues if i.code == "fringe_threshold_undetermined"
        ]
        assert issue.fact is None
        assert "fringe_threshold_undetermined" in {b.detail for b in result.blockers}

    def test_unknown_children_within_both_thresholds_is_final(self) -> None:
        """400 is exempt against either threshold: nothing is missing."""
        result = _run(3, _D(400), family=None)
        (decision,) = _decisions(result)
        assert decision.status is CalculationStatus.FINAL
        assert "fringe_threshold_undetermined" not in {i.code for i in result.issues}

    def test_a_known_child_settles_an_unknown_one(self) -> None:
        """One child within the limit is enough: the other is not needed."""
        unknown = replace(_CHILD, own_income=None)
        family = FamilyComposition(dependents=(unknown, _CHILD))
        result = _run(3, _D(1500), family=family)
        assert _item(result).threshold_annual == _WITH_CHILDREN
        assert _decisions(result)[0].status is CalculationStatus.FINAL


# ---------------------------------------------------------------------------
# due fringe da 200 con soglia 258,23 — imponibile 0.00 invece di 400.00
# ---------------------------------------------------------------------------


def test_cumulative_fringe_threshold() -> None:
    """Two fringe events whose cumulative sum exceeds the threshold are taxable.

    Two FringeEvent(600) in the same period: cumulative = 1200, which exceeds
    the 2026 standard threshold (1000 EUR under L. 207/2024). Both amounts must
    become taxable, increasing ORDINARY_TAX relative to a no-fringe baseline.
    """
    event_date = date(_YEAR, 1, 15)
    fringe_a = FringeEvent(event_date=event_date, amount=Decimal("600.00"))
    fringe_b = FringeEvent(event_date=event_date, amount=Decimal("600.00"))
    result_with_fringe = calculate_period(period_request(events=(fringe_a, fringe_b)))
    result_without = calculate_period(period_request())

    tax_with = account_total(result_with_fringe, AccountKind.ORDINARY_TAX)
    tax_without = account_total(result_without, AccountKind.ORDINARY_TAX)

    assert tax_with > tax_without, (
        f"ORDINARY_TAX with cumulative fringe ({tax_with}) must exceed "
        f"base case ({tax_without}): two fringe events at 600 (total 1200) "
        "exceed the 2026 threshold (1000) and must be fully taxable."
    )


# ---------------------------------------------------------------------------
# cross-period fringe retroactive adjustment missing
#
# L. 207/2024 art. 1 c. 390 (derogating TUIR art. 51 c. 3; AdE circ. 4/E/2025
# par. 2.7): when the annual cumulated fringe benefit exceeds
# the threshold, the ENTIRE annual cumulated amount is subject to INPS and
# IRPEF — including amounts that were previously exempt.  When fringe_ytd=600
# (exempt month 1) and a second FringeEvent(600) crosses the 1,000 EUR
# threshold in month 2, the engine must retroactively tax the prior 600 and
# report irpef_base = 1,200 for the combined period.
# ---------------------------------------------------------------------------


def test_fringe_retroactive_on_threshold_crossing() -> None:
    """irpef_base must cover the full cumulative fringe when crossing.

    Source: L. 207/2024 art. 1 c. 390.  fringe_ytd=600 + FringeEvent(600) =
    1,200 > 1,000 threshold → irpef_base must equal 1,200 (full retroactive).
    """
    state_after_m1 = PeriodState(
        cash=TaxCashState(
            fringe=FringeYtd(value=Decimal("600.00")),
        )
    )
    fringe = FringeEvent(event_date=date(_YEAR, 2, 15), amount=Decimal("600.00"))
    result = calculate_period(
        period_request(month=2, opening=state_after_m1, events=(fringe,))
    )

    assert result.benefit_breakdown.irpef_base == Decimal("1200.00"), (
        "irpef_base after threshold crossing must be 1,200 (full cumulative "
        f"retroactive); got {result.benefit_breakdown.irpef_base}."
    )
