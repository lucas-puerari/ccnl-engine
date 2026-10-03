"""Fringe benefit threshold and taxable amount, through the public API.

Rule (2026): L. 207/2024 art. 1 c. 390, in derogation of TUIR art. 51 c. 3,
exempts goods and services granted to an employee "entro il limite
complessivo di 1.000 euro" per tax year for 2025, 2026 and 2027, raised to
2.000 euro for a worker with a fiscally dependent child (art. 12 c. 2 TUIR)
who declares it to the employer (c. 391).  AdE circolare 4/E of 16 May 2025,
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

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    FringeEvent,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
    PeriodState,
)
from ccnl_engine.payroll.application.period._capability_traces import build_traces
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.pay_items import FringeBenefitItem

engine = PayrollEngine.bundled()

_D = Decimal
_YEAR = 2026
_STANDARD = _D(1000)
_WITH_CHILDREN = _D(2000)


def _run(
    month: int,
    *amounts: Decimal,
    children: bool = False,
    opening: PeriodState | None = None,
) -> PeriodResult:
    events = tuple(
        FringeEvent(event_date=date(_YEAR, month, 1), amount=a) for a in amounts
    )
    return engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=_YEAR, month=month),
            payment_date=date(_YEAR, month, 27),
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
            ),
            employer=EmployerProfile(headcount=Headcount(100)),
            facts=PeriodFacts(events=events, has_dependent_children=children),
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
            result.closing_state.cash.earnings.inps_base
            - base.closing_state.cash.earnings.inps_base
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
