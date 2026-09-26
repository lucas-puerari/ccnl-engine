"""Capability traces follow what a run executed, not what the request holds."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.capability_catalog import CapabilityGapKind
from ccnl_engine.engine.contract.domain.category import WorkerCategory
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.tax.service.loaders import load_variable_pay_rules
from ccnl_engine.payroll.application._capability_traces import build_traces
from ccnl_engine.payroll.application._run_decisions import worker_category_decision
from ccnl_engine.payroll.application.allocate_events import _process_events
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import calculate_year
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import SeniorityMonths
from ccnl_engine.payroll.domain.employment_context import EffectiveDateContext
from ccnl_engine.payroll.domain.events import (
    BonusEvent,
    OvertimeEvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
from ccnl_engine.payroll.domain.prior_year import PriorYearTaxFacts
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.trace import TraceState
from ccnl_engine.payroll.domain.ytd_accounts import FringeYtd
from tests.helpers import year_input

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.decisions import CalculationDecision

_D = Decimal
_YEAR = 2026
_DATE = date(_YEAR, 1, 15)
_PAYMENT = date(_YEAR, 1, 28)
_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_COMMERCIO = "commercio-confcommercio.json"
_FISE = "servizi-postali-appalto-fise.json"
_RESOLVER = PolicyResolver.load()
_PDR = load_variable_pay_rules(_YEAR).pdr


def _run(
    ccnl_slug: str = _METALMECCANICO, level_code: str = "C3", **kwargs: object
) -> PeriodResult:
    request = PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=1),
        payment_date=_PAYMENT,
        ccnl_slug=ccnl_slug,
        level_code=level_code,
        employer=kwargs.pop("employer", EmployerProfile(headcount=Headcount(50))),  # type: ignore[arg-type]
        opening_state=kwargs.pop("opening_state", PeriodState.zero()),  # type: ignore[arg-type]
        **kwargs,  # type: ignore[arg-type]
    )
    return calculate_period(request, resolver=_RESOLVER)


def _decisions(result: PeriodResult, capability: str) -> list[CalculationDecision]:
    return [d for d in result.decisions if d.capability == capability]


def _executed(*events: WorkEvent) -> frozenset[str]:
    totals, _, _ = _process_events(
        events,
        CompetencePeriod(year=_YEAR, month=1),
        _PAYMENT,
        "t",
        EffectiveDateContext.from_period(_YEAR, 1, _PAYMENT),
        _RESOLVER,
        PolicyContext(year=_YEAR, as_of=date(_YEAR, 1, 1)),
    )
    return totals.executed_features


class TestEventExecution:
    """An event feature is computed only when its handler had an effect."""

    def test_event_without_effect_is_not_computed(self) -> None:
        """A zero welfare event is present in the request but did nothing."""
        executed = _executed(WelfareEvent(event_date=_DATE, amount=_D(0)))
        assert executed == frozenset()
        states = {t.feature: t.state for t in build_traces((), executed)}
        assert states["welfare"] is TraceState.SKIPPED

    def test_event_with_effect_is_computed(self) -> None:
        """A posted welfare event computes its feature and only that one."""
        executed = _executed(
            WelfareEvent(event_date=_DATE, amount=_D(0)),
            OvertimeEvent(event_date=_DATE, hours=_D(2), hourly_rate=_D(15)),
        )
        assert executed == frozenset({"overtime"})

    def test_bonus_has_no_event_feature(self) -> None:
        """A bonus is traced through its PdR decision, not as an event."""
        assert _executed(BonusEvent(event_date=_DATE, amount=_D(500))) == frozenset()


class TestTaxCreditDecisions:
    """The run records the trattamento and ulteriore detrazione decisions."""

    def test_credits_decided_on_every_run(self) -> None:
        """Both credits are decided, with the reason of their amount."""
        result = _run()
        (ulteriore,) = _decisions(result, "ulteriore_detrazione_lavoro")
        (trattamento,) = _decisions(result, "trattamento_integrativo")
        assert ulteriore.reason_code == "full_amount"
        assert trattamento.reason_code in {
            "deductions_above_irpef",
            "deductions_not_above_irpef",
        }
        credit = sum(
            (
                c.amount
                for c in result.tax_computation.components
                if c.name == "trattamento_integrativo"
            ),
            _D(0),
        )
        assert trattamento.amount == credit


class TestWorkerCategoryDecision:
    """The category used and its origin are recorded."""

    def test_declared_category(self) -> None:
        """A category declared on an open level has origin ``declared``."""
        result = _run(
            _FISE,
            "2",
            category=WorkerCategory.IMPIEGATO,
            seniority_months=SeniorityMonths(60),
        )
        (decision,) = _decisions(result, "worker_category")
        assert decision.reason_code == "declared"
        assert decision.inputs["category"] == "impiegato"
        assert decision.inputs["declared"] == "impiegato"

    def test_category_fixed_by_level(self) -> None:
        """A single-category level fixes the category without a declaration."""
        (decision,) = _decisions(_run(_COMMERCIO, "Q"), "worker_category")
        assert decision.reason_code == "fixed_by_level"
        assert decision.inputs == {
            "category": "quadro",
            "declared": "none",
            "level": "Q",
        }

    def test_no_category_used_takes_no_decision(self) -> None:
        """Without a category nothing is decided."""
        assert _decisions(_run(_COMMERCIO, "4"), "worker_category") == []

    def test_ccnl_without_ruleset_is_versioned_by_year(self) -> None:
        """The CCNL slug and the year identify the rule without a ruleset."""
        ccnl = load_ccnl(_COMMERCIO).model_copy(update={"ruleset": None})
        decision = worker_category_decision(
            ccnl, ccnl.level_by_code("Q"), None, WorkerCategory.QUADRO, _YEAR
        )
        assert decision is not None
        assert decision.rule == f"ccnl/{ccnl.meta.ccnl_id}"
        assert decision.rule_version == "2026"


class TestSeniorityDecision:
    """Seniority is decided only when the months of service are known."""

    def test_increments_applied(self) -> None:
        """Months of service with increments due record the run amount."""
        (decision,) = _decisions(
            _run(seniority_months=SeniorityMonths(60)), "seniority"
        )
        assert decision.reason_code == "increments_applied"
        assert decision.amount is not None
        assert decision.amount > 0

    def test_no_increment_due(self) -> None:
        """Months of service below the first increment decide a zero."""
        (decision,) = _decisions(_run(seniority_months=SeniorityMonths(0)), "seniority")
        assert decision.reason_code == "no_increment_due"
        assert decision.amount == _D(0)

    def test_unknown_months_take_no_decision(self) -> None:
        """Without months of service nothing is decided."""
        assert _decisions(_run(), "seniority") == []


class TestFamilyDeductionDecision:
    """Family deductions are decided only with a family composition."""

    def test_deductions_applied(self) -> None:
        """A dependent spouse yields a positive annual deduction."""
        family = FamilyComposition(
            dependents=(Dependent(relationship=DependentRelationship.SPOUSE),)
        )
        (decision,) = _decisions(_run(family_composition=family), "family_deductions")
        assert decision.reason_code == "deductions_applied"
        assert decision.amount is not None
        assert decision.amount > 0

    def test_no_dependents(self) -> None:
        """An empty family composition decides a zero deduction."""
        (decision,) = _decisions(
            _run(family_composition=FamilyComposition()), "family_deductions"
        )
        assert decision.reason_code == "no_deduction_due"
        assert decision.amount == _D(0)

    def test_no_composition_takes_no_decision(self) -> None:
        """Without a family composition nothing is decided."""
        assert _decisions(_run(), "family_deductions") == []


class TestPdrDecision:
    """The PdR substitute tax is decided only for a bonus routed to it."""

    _BONUS = BonusEvent(event_date=_DATE, amount=_D(1000), kind="productivity_bonus")
    _PRIOR = PriorYearTaxFacts(employment_income=_D(30000))

    def test_substitute_tax_applied(self) -> None:
        """An eligible productivity bonus records the substitute tax."""
        (decision,) = _decisions(
            _run(events=(self._BONUS,), prior_year=self._PRIOR), "bonus_pdr"
        )
        assert decision.reason_code == "substitute_tax_applied"
        assert decision.amount == _D(1000) * _PDR.flat_tax_rate
        assert decision.inputs["eligible_amount"] == _D(1000)

    def test_annual_limit_reached(self) -> None:
        """A bonus over an exhausted annual limit decides a zero tax."""
        opening = PeriodState(ytd=TaxYearState(fringe=FringeYtd(pdr=_PDR.max_amount)))
        (decision,) = _decisions(
            _run(events=(self._BONUS,), opening_state=opening, prior_year=self._PRIOR),
            "bonus_pdr",
        )
        assert decision.reason_code == "annual_limit_reached"
        assert decision.amount == _D(0)
        assert decision.inputs["ordinary_amount"] == _D(1000)

    def test_no_bonus_takes_no_decision(self) -> None:
        """Without a bonus routed to the substitute tax nothing is decided."""
        assert _decisions(_run(), "bonus_pdr") == []


class TestReportGaps:
    """The capability report flags a capability that could not decide."""

    def test_unknown_surtax_table_is_an_unresolved_gap(self) -> None:
        """An unknown surtax table is a gap, not a computed capability."""
        result = _run(regione="IT-99", comune_belfiore="Z999")
        unresolved = {
            g.feature
            for g in result.capability_report.gaps
            if g.kind is CapabilityGapKind.UNRESOLVED
        }
        assert unresolved == {"addizionale_regionale", "addizionale_comunale"}

    def test_known_surtax_tables_are_not_gaps(self) -> None:
        """Known tables keep the surtax out of the gaps."""
        result = _run(regione="IT-45", comune_belfiore="F257")
        features = {g.feature for g in result.capability_report.gaps}
        assert not features & {"addizionale_regionale", "addizionale_comunale"}


class TestYearDecisions:
    """The year result exposes the decisions of its runs."""

    def test_year_decisions_concatenate_runs(self) -> None:
        """Year decisions are the run decisions in payment order."""
        year = calculate_year(
            year_input(_YEAR, _METALMECCANICO, "C3"), resolver=_RESOLVER
        )
        runs = year.period_results
        assert year.decisions == tuple(d for r in runs for d in r.decisions)
        assert len(year.decisions) == 3 * len(runs)
