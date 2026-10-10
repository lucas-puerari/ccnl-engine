"""Somma esente of a run: share, conguaglio and recovery (L. 207/2024 art. 1)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.amount.facade import CompetencePeriod
from ccnl_engine.payroll.amount.loaders_policy import load_policy_resolver
from ccnl_engine.payroll.amount.policies import PolicyContext
from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.models_credit_account import SommaEsenteAccount
from ccnl_engine.payroll.state.models_obligation import (
    SOMMA_ESENTE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.state.models_tax_cash import TaxCashState
from ccnl_engine.payroll.taxation.inputs_current_year import CurrentYearTaxFacts
from ccnl_engine.payroll.taxation.results import TaxComputation, TaxLineItem
from ccnl_engine.payroll.withholding.models_recovery_plan import (
    InstallmentRun,
    RecoveryPlan,
)
from ccnl_engine.payroll.withholding.models_schedule import WithholdingPosition
from ccnl_engine.payroll.withholding.services_somma_esente import (
    SommaEsenteOutcome,
    SommaEsentePosting,
    resolve_somma_esente,
)
from ccnl_engine.tax.income.models_credit import SommaEsenteBand, SommaEsenteRules
from tests.integration.ccnl_engine.payroll.period.builders_period_requests import (
    account_total,
    period_request,
)
from tests.unit.ccnl_engine.builders import make_year_rules

if TYPE_CHECKING:
    from ccnl_engine.tax.annual.models import YearRules

_ZERO = Decimal(0)
_YEAR = 2026
# 12 slots, one per regular month.
_SLOTS = 12
_RULES = make_year_rules().model_copy(
    update={
        "somma_esente": SommaEsenteRules(
            bands=[SommaEsenteBand(up_to=Decimal(20000), rate=Decimal("0.07"))]
        )
    }
)
#: No income beyond this employment in 2026: the reddito complessivo of
#: L. 207/2024 art. 1 c. 4 is the employment income.
_EMPLOYMENT_ONLY = CurrentYearTaxFacts.employment_only(_YEAR, date(_YEAR, 1, 1))
_POSTING = SommaEsentePosting(
    resolver=load_policy_resolver(),
    policy_context=PolicyContext(year=_YEAR, as_of=date(_YEAR, 12, 1)),
    competence_period=CompetencePeriod(year=_YEAR, month=12),
    payment_date=date(_YEAR, 12, 28),
    run_id="2026-12-thirteenth",
)


def _tax(annual: Decimal | None, period: Decimal = Decimal(100)) -> TaxComputation:
    """Return a computation with the annual somma esente and its run share.

    ``period`` is the percentage applied to the income the run pays (AdE
    circ. 4/E/2025 par. 1.2).

    Returns:
        The computation, without somma esente when ``annual`` is ``None``.
    """
    components = (
        ()
        if annual is None
        else (
            TaxLineItem(
                name="somma_esente", amount=annual, rule_id="r", fonte="L. 207/2024"
            ),
            TaxLineItem(
                name="somma_esente_period", amount=period, rule_id="r", fonte="4/E"
            ),
        )
    )
    return TaxComputation(
        ordinary_tax=_ZERO,
        trattamento_integrativo=_ZERO,
        withholding_due=_ZERO,
        components=components,
    )


def _opening(
    *,
    recognized: Decimal = _ZERO,
    recovered: Decimal = _ZERO,
    plan: RecoveryPlan | None = None,
) -> PeriodState:
    obligations = (
        EmploymentObligations()
        if plan is None
        else EmploymentObligations(
            recoveries=(RecoveryObligation(tax_year=_YEAR, plan=plan),)
        )
    )
    return PeriodState(
        cash=TaxCashState(
            tax_year=_YEAR,
            somma_esente=SommaEsenteAccount(recognized=recognized, recovered=recovered),
            obligations=obligations,
        )
    )


def _position(closed: int) -> WithholdingPosition:
    """Return the position of a run after ``closed`` of the twelve slots.

    Returns:
        The position, settling the conguaglio on the last slot.
    """
    remaining = max(1, _SLOTS - closed)
    return WithholdingPosition(
        slots=_SLOTS, remaining=remaining, upcoming=(), settles=remaining == 1
    )


def _resolve(
    annual: Decimal | None,
    opening: PeriodState,
    rules: YearRules = _RULES,
    *,
    closed: int,
    current_year: CurrentYearTaxFacts | None = _EMPLOYMENT_ONLY,
    period: Decimal = Decimal(100),
) -> SommaEsenteOutcome:
    return resolve_somma_esente(
        _tax(annual, period),
        rules,
        opening,
        _position(closed),
        _YEAR,
        _POSTING,
        current_year,
    )


class TestBeforeTheConguaglio:
    """A run before the last slot pays its share, never more than still due."""

    def test_pays_the_share_of_the_income_of_the_run(self) -> None:
        """1,200 EUR due in the year, 100.00 on the income of the run."""
        outcome = _resolve(Decimal(1200), _opening(), closed=0)

        assert outcome.amount == Decimal("100.00")
        assert outcome.due == Decimal("1200.00")
        assert outcome.reason == "share_paid"
        assert outcome.items[0].item_id == "somma_esente_2026-12-thirteenth"
        (entry,) = outcome.entries
        assert (entry.account, entry.amount) == (AccountKind.CREDITS, Decimal(100))
        assert entry.remittance_code == "1704"

    def test_caps_the_share_at_what_is_still_due(self) -> None:
        """1,150 paid of 1,200 due: the run pays the 50 left, not 100."""
        outcome = _resolve(Decimal(1200), _opening(recognized=Decimal(1150)), closed=5)

        assert outcome.amount == Decimal(50)

    def test_a_larger_payment_pays_a_larger_share(self) -> None:
        """A tredicesima doubles the income of the run: 200.00, not 1200/12."""
        outcome = _resolve(Decimal(1200), _opening(), closed=5, period=Decimal(200))

        assert outcome.amount == Decimal(200)
        assert outcome.decisions[0].inputs["period_share"] == Decimal(200)

    def test_holds_an_excess_until_the_conguaglio(self) -> None:
        """The due fell below what was paid: nothing paid, nothing recovered."""
        outcome = _resolve(Decimal(300), _opening(recognized=Decimal(600)), closed=6)

        assert outcome.amount == _ZERO
        assert outcome.reason == "overpayment_pending_conguaglio"
        assert outcome.items == ()
        assert outcome.decisions[0].inputs["net_paid_before"] == Decimal(600)

    def test_not_due_on_income_above_the_bands(self) -> None:
        """No component: zero, with a decision saying so."""
        outcome = _resolve(None, _opening(), closed=0)

        assert outcome.amount == _ZERO
        assert outcome.due == _ZERO
        assert outcome.reason == "not_due"
        assert outcome.decisions[0].capability == "somma_esente"
        assert outcome.issues == ()

    def test_stated_income_beyond_the_employment_raises_no_issue(self) -> None:
        """With the income of the year stated, the reddito complessivo is known."""
        outcome = _resolve(Decimal(1200), _opening(), closed=0)

        assert outcome.issues == ()

    def test_unknown_income_beyond_the_employment_is_a_missing_fact(self) -> None:
        """Other income may remove the entitlement (c. 4): current_year is named."""
        outcome = _resolve(Decimal(1200), _opening(), closed=0, current_year=None)

        (issue,) = outcome.issues
        assert issue.code == "somma_esente_income_unknown"
        assert issue.status is CalculationStatus.INCOMPLETE
        assert issue.fact == "current_year"

    def test_income_facts_of_another_year_are_not_used(self) -> None:
        """Facts of 2025 do not state the reddito complessivo of 2026."""
        stale = CurrentYearTaxFacts.employment_only(_YEAR - 1, date(_YEAR - 1, 1, 1))
        outcome = _resolve(Decimal(1200), _opening(), closed=0, current_year=stale)

        assert [i.fact for i in outcome.issues] == ["current_year"]

    def test_unknown_income_matters_only_while_an_amount_is_due(self) -> None:
        """Nothing due on this employment: more income cannot make it due."""
        outcome = _resolve(None, _opening(), closed=0, current_year=None)

        assert outcome.issues == ()

    @pytest.mark.parametrize(
        "other",
        [
            replace(_EMPLOYMENT_ONLY, other_employment_income=Decimal(3000)),
            replace(_EMPLOYMENT_ONLY, exempt_regime_income=Decimal(3000)),
        ],
        ids=["other_employment_income", "exempt_regime_income"],
    )
    def test_band_is_provisional_with_income_of_other_employers(
        self, other: CurrentYearTaxFacts
    ) -> None:
        """The band of c. 4 is taken on this employer's income alone.

        Exempt income of the impatriati and researcher regimes counts in
        the reddito di lavoro dipendente of c. 4 (L. 207/2024 c. 9).
        """
        outcome = _resolve(Decimal(1200), _opening(), closed=0, current_year=other)

        (issue,) = outcome.issues
        assert issue.code == "somma_esente_band_assumed"
        assert issue.status is CalculationStatus.PROVISIONAL
        assert issue.fact is None


class TestAtTheConguaglio:
    """The last slot settles the balance and recovers an over-payment."""

    def test_pays_the_balance(self) -> None:
        """The last slot pays exactly the due not yet paid, cents included."""
        outcome = _resolve(
            Decimal("877.04064"),
            _opening(recognized=Decimal("809.52")),
            closed=_SLOTS - 1,
        )

        assert outcome.amount == Decimal("67.52")
        assert outcome.reason == "settled_at_conguaglio"

    def test_recovers_up_to_60_eur_in_full(self) -> None:
        """40 EUR paid in excess are recovered on the conguaglio payslip."""
        outcome = _resolve(
            Decimal(500), _opening(recognized=Decimal(540)), closed=_SLOTS - 1
        )

        assert outcome.amount == Decimal(-40)
        assert outcome.reason == "overpayment_recovered"
        assert outcome.plan is None
        assert outcome.items[0].item_id == "somma_esente_recovery_2026-12-thirteenth"
        (entry,) = outcome.entries
        assert (entry.account, entry.amount) == (
            AccountKind.CREDIT_RECOVERIES,
            Decimal(40),
        )
        assert entry.remittance_code == "1704"

    def test_recovers_above_60_eur_in_ten_installments(self) -> None:
        """150 EUR in excess: 15 EUR now, nine installments left."""
        outcome = _resolve(
            Decimal(500), _opening(recognized=Decimal(650)), closed=_SLOTS - 1
        )

        assert outcome.amount == Decimal("-15.00")
        assert outcome.reason == "overpayment_recovery_opened"
        assert outcome.plan == RecoveryPlan(
            kind=SOMMA_ESENTE_RECOVERY,
            original_amount=Decimal(150),
            installment_amount=Decimal("15.00"),
            installments_total=10,
            installments_posted=1,
        )

    def test_net_of_what_was_already_recovered(self) -> None:
        """Recovered credit is not recovered twice."""
        outcome = _resolve(
            Decimal(500),
            _opening(recognized=Decimal(540), recovered=Decimal(40)),
            closed=_SLOTS - 1,
        )

        assert outcome.amount == _ZERO
        assert outcome.reason == "settled_at_conguaglio"


class TestRunningRecovery:
    """A plan of the current year posts its installment on every later run."""

    _PLAN = RecoveryPlan.create(SOMMA_ESENTE_RECOVERY, Decimal(150), 10)

    def test_posts_the_next_installment(self) -> None:
        """The plan, not the projection, sets the amount."""
        plan = self._PLAN.advance()
        outcome = _resolve(Decimal(500), _opening(plan=plan), closed=_SLOTS)

        assert outcome.amount == Decimal("-15.00")
        assert outcome.reason == "installment_posted"
        assert outcome.plan == plan.advance()
        assert outcome.decisions[0].inputs["recovery_in_progress"] == "true"

    def test_last_installment_closes_the_plan(self) -> None:
        """After the last installment no plan is left."""
        plan = replace(self._PLAN, installments_posted=9)
        outcome = _resolve(Decimal(500), _opening(plan=plan), closed=_SLOTS)

        assert outcome.amount == Decimal("-15.00")
        assert outcome.reason == "last_installment_posted"
        assert outcome.plan is None


class TestNotInForce:
    """Without rules and nothing paid there is nothing to decide."""

    def test_returns_an_empty_outcome(self) -> None:
        """No amount, no posting, no decision."""
        rules = _RULES.model_copy(update={"somma_esente": None})

        assert _resolve(None, _opening(), rules, closed=0) == SommaEsenteOutcome()

    def test_still_settles_what_was_paid(self) -> None:
        """Credit paid under rules no longer in force is recovered at conguaglio."""
        rules = _RULES.model_copy(update={"somma_esente": None})
        outcome = _resolve(
            None, _opening(recognized=Decimal(30)), rules, closed=_SLOTS - 1
        )

        assert outcome.amount == Decimal(-30)
        assert outcome.reason == "overpayment_recovered"


class TestLastRunOfTheEmployment:
    """On the last run of the employment nothing is left to installments."""

    def test_recovers_the_whole_excess(self) -> None:
        """150 EUR in excess are recovered at once, above 60 EUR too."""
        outcome = _resolve_on(
            InstallmentRun(final=True),
            _opening(recognized=Decimal(650)),
            closed=_SLOTS - 1,
        )

        assert outcome.amount == Decimal(-150)
        assert outcome.reason == "overpayment_recovered_at_termination"
        assert outcome.plan is None

    def test_adjustment_run_posts_the_next_installment(self) -> None:
        """A plan of 150, 15 per installment, one posted: the run posts 15."""
        plan = RecoveryPlan.create(SOMMA_ESENTE_RECOVERY, Decimal(150), 10).advance()
        outcome = _resolve_on(
            InstallmentRun(adjustment=True),
            _opening(recognized=Decimal(650), plan=plan),
            closed=_SLOTS,
        )

        assert outcome.amount == Decimal("-15.00")
        assert outcome.reason == "installment_posted_adjustment_run"
        assert outcome.plan == plan.advance()


def _resolve_on(
    run: InstallmentRun, opening: PeriodState, *, closed: int
) -> SommaEsenteOutcome:
    return resolve_somma_esente(
        _tax(Decimal(500)),
        _RULES,
        opening,
        _position(closed),
        _YEAR,
        replace(_POSTING, run=run),
        _EMPLOYMENT_ONLY,
    )


# ---------------------------------------------------------------------------
# somma_esente computed but never posted to CREDITS ledger
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
        period_request(
            month=6, ccnl="acconciatura-estetica-confartigianato.json", level="3"
        )
    )
    tax_credits = account_total(result, AccountKind.CREDITS)
    assert tax_credits > _ZERO, (
        f"CREDITS for a low-income worker (acconciatura-estetica level 3) must "
        f"be > 0 due to the somma_esente credit (L. 160/2019); got {tax_credits}.  "
        "calculate_period posts only trattamento_integrativo to CREDITS and "
        "ignores the somma_esente component from TaxComputation."
    )
