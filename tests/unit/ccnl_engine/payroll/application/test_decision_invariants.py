"""Decision invariants: plafond, substitute-tax eligibility and provenance."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine.engine.tax.domain.preferential_regime import EmploymentSector
from ccnl_engine.payroll.application._reconcile_types import RunFacts
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.decision_invariants import (
    check_decision_provenance,
    check_substitute_tax_eligibility,
    check_substitute_tax_plafond,
)
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.employer import (
    EmployerActivity,
    EmployerProfile,
    Headcount,
)
from ccnl_engine.payroll.domain.events import BonusEvent, NightShiftEvent
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.ytd_accounts import FringeYtd

_YEAR = 2026
_OPENING = PeriodState.zero()
_PLAFOND = "substitute_tax_plafond"
_ELIGIBILITY = "substitute_tax_eligibility"


def _run(*events: NightShiftEvent | BonusEvent, income: int = 20_000) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(50), activity=EmployerActivity.OTHER
            ),
            period_id=PeriodId(year=_YEAR, month=3),
            payment_date=date(_YEAR, 3, 27),
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            events=events,
            sector=EmploymentSector.PRIVATE,
            prior_year=PriorYearTaxFacts(employment_income=Decimal(income)),
        )
    )


def _night(amount: int) -> NightShiftEvent:
    return NightShiftEvent(
        event_date=date(_YEAR, 3, 10), supplement_amount=Decimal(amount)
    )


_PDR_BONUS = BonusEvent(
    event_date=date(_YEAR, 3, 10), amount=Decimal(1_000), kind="productivity_bonus"
)
_PDR_INCOME = 30_000


def _with_decisions(
    result: PeriodResult, *decisions: CalculationDecision
) -> PeriodResult:
    return replace(result, decisions=decisions)


def _regime_decision(result: PeriodResult) -> CalculationDecision:
    return next(d for d in result.decisions if d.capability.endswith("_substitute_tax"))


class TestPlafondChain:
    """Each capped decision sees the cap the previous decisions left."""

    def test_two_supplements_pass(self) -> None:
        """Two supplements over the cap chain their cap_available."""
        result = _run(_night(1_000), _night(1_000))
        assert check_substitute_tax_plafond(result, _OPENING, RunFacts()) == []
        assert reconcile(result, _OPENING).ok

    def test_wrong_cap_available_is_reported(self) -> None:
        """A cap_available that ignores the earlier eligible amount is caught."""
        result = _run(_night(1_000), _night(1_000))
        first, second = [
            d for d in result.decisions if d.capability.endswith("_substitute_tax")
        ]
        bad_second = replace(
            second,
            inputs={**second.inputs, "cap_available": Decimal(1_500)},
        )
        others = [d for d in result.decisions if d is not first and d is not second]
        bad = _with_decisions(result, *others, first, bad_second)

        violations = check_substitute_tax_plafond(bad, _OPENING, RunFacts())
        (chain,) = [v for v in violations if "cap_available" in v.message]
        assert chain.invariant_id == _PLAFOND
        assert chain.expected == Decimal(500)
        assert chain.actual == Decimal(1_500)

    def test_eligible_above_cap_left_is_reported(self) -> None:
        """An eligible amount above the cap it saw is a violation."""
        result = _run(_night(2_000))
        decision = _regime_decision(result)
        bad_decision = replace(
            decision,
            inputs={**decision.inputs, "eligible_amount": Decimal(1_600)},
        )
        others = [d for d in result.decisions if d is not decision]
        bad = _with_decisions(result, *others, bad_decision)

        messages = [
            v.message for v in check_substitute_tax_plafond(bad, _OPENING, RunFacts())
        ]
        assert any("exceeds the cap left" in m for m in messages)


class TestPdrPlafond:
    """The PdR eligible YTD advances by the run and stays within its limit."""

    def test_real_pdr_run_passes(self) -> None:
        """A real PdR bonus advances fringe.pdr by its eligible amount."""
        result = _run(_PDR_BONUS, income=_PDR_INCOME)
        facts = RunFacts(pdr_cap=Decimal(5_000))
        assert result.closing_state.ytd.fringe.pdr == Decimal(1_000)
        assert check_substitute_tax_plafond(result, _OPENING, facts) == []

    def test_wrong_advance_is_reported(self) -> None:
        """A closing fringe.pdr that ignores the decision is a violation."""
        result = _run(_PDR_BONUS, income=_PDR_INCOME)
        ytd = result.closing_state.ytd
        closing = replace(
            result.closing_state,
            ytd=replace(ytd, fringe=replace(ytd.fringe, pdr=Decimal(0))),
        )
        bad = replace(result, closing_state=closing)

        (violation,) = check_substitute_tax_plafond(bad, _OPENING, RunFacts())
        assert violation.invariant_id == _PLAFOND
        assert violation.expected == Decimal(1_000)

    def test_ytd_above_limit_is_reported(self) -> None:
        """A PdR YTD above the annual limit is a violation."""
        result = _run(_PDR_BONUS, income=_PDR_INCOME)
        facts = RunFacts(pdr_cap=Decimal(500))

        (violation,) = check_substitute_tax_plafond(result, _OPENING, facts)
        assert violation.invariant_id == _PLAFOND
        assert violation.expected == Decimal(500)
        assert violation.actual == Decimal(1_000)

    def test_opening_pdr_is_carried(self) -> None:
        """The advance starts from the opening PdR YTD."""
        result = _run(_PDR_BONUS, income=_PDR_INCOME)
        opening = PeriodState(
            ytd=replace(_OPENING.ytd, fringe=FringeYtd(pdr=Decimal(100)))
        )
        (violation,) = check_substitute_tax_plafond(result, opening, RunFacts())
        assert violation.expected == Decimal(1_100)


class TestSubstituteTaxEligibility:
    """Substitute tax is posted only on amounts an eligible decision covers."""

    def test_real_runs_pass(self) -> None:
        """Eligible, ineligible and PdR runs agree with their postings."""
        for result in (
            _run(_night(500)),
            _run(_night(500), income=50_000),
            _run(_PDR_BONUS, income=_PDR_INCOME),
            _run(),
        ):
            assert check_substitute_tax_eligibility(result) == []

    def test_ineligible_decision_with_eligible_amount_is_reported(self) -> None:
        """An ineligible decision that taxes an amount is a violation."""
        result = _run(_night(500))
        decision = _regime_decision(result)
        bad_decision = replace(
            decision, inputs={**decision.inputs, "eligibility": "ineligible"}
        )
        others = [d for d in result.decisions if d is not decision]
        bad = _with_decisions(result, *others, bad_decision)

        (violation,) = check_substitute_tax_eligibility(bad)
        assert violation.invariant_id == _ELIGIBILITY
        assert "ineligible" in violation.message
        assert violation.actual == Decimal(500)

    def test_tax_on_nil_eligible_amount_is_reported(self) -> None:
        """A decision taxing a nil eligible amount is a violation."""
        result = _run(_PDR_BONUS, income=_PDR_INCOME)
        decision = next(d for d in result.decisions if d.capability == "bonus_pdr")
        bad_decision = replace(
            decision, inputs={**decision.inputs, "eligible_amount": Decimal(0)}
        )
        others = [d for d in result.decisions if d is not decision]
        bad = _with_decisions(result, *others, bad_decision)

        (violation,) = check_substitute_tax_eligibility(bad)
        assert violation.invariant_id == _ELIGIBILITY
        assert "no eligible amount" in violation.message

    def test_posting_without_decision_is_reported(self) -> None:
        """SUBSTITUTE_TAX posted without a decision is a violation."""
        result = _run(_night(500))
        decision = _regime_decision(result)
        bad = _with_decisions(
            result, *(d for d in result.decisions if d is not decision)
        )

        (violation,) = check_substitute_tax_eligibility(bad)
        assert violation.invariant_id == _ELIGIBILITY
        assert violation.expected == Decimal(0)
        assert violation.actual == decision.amount


class TestDecisionProvenance:
    """Every final decision names its rule and rule version."""

    def test_real_run_passes(self) -> None:
        """Every decision of a real run carries its provenance."""
        assert check_decision_provenance(_run(_night(500), _PDR_BONUS)) == []

    def test_blank_rule_version_is_reported(self) -> None:
        """A final decision with a blank rule version is a violation."""
        result = _run(_PDR_BONUS, income=_PDR_INCOME)
        decision = next(d for d in result.decisions if d.capability == "bonus_pdr")
        object.__setattr__(decision, "rule_version", " ")  # noqa: PLC2801

        (violation,) = check_decision_provenance(result)
        assert violation.invariant_id == "decision_provenance"
        assert "bonus_pdr" in violation.message

    def test_provisional_decision_is_not_checked(self) -> None:
        """Only final decisions must carry a rule and version."""
        result = _run(_PDR_BONUS, income=_PDR_INCOME)
        decision = replace(
            next(d for d in result.decisions if d.capability == "bonus_pdr"),
            status=CalculationStatus.PROVISIONAL,
        )
        object.__setattr__(decision, "rule", " ")  # noqa: PLC2801
        assert check_decision_provenance(_with_decisions(result, decision)) == []
