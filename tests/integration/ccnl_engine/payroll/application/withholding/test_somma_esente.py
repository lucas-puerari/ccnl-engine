"""Somma esente of a run: share, conguaglio and recovery (L. 207/2024 art. 1)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.withholding._somma_esente import (
    SommaEsenteOutcome,
    SommaEsentePosting,
    resolve_somma_esente,
)
from ccnl_engine.payroll.domain.credit_accounts import SommaEsenteAccount
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import (
    SOMMA_ESENTE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.policy import PolicyContext
from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun, RecoveryPlan
from ccnl_engine.payroll.domain.tax import TaxComputation, TaxLineItem
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.withholding_schedule import WithholdingPosition
from ccnl_engine.payroll.service.policy_loader import load_policy_resolver
from ccnl_engine.tax.domain.credit_rules import SommaEsenteBand, SommaEsenteRules
from tests.fixtures.period_requests import account_total, period_request
from tests.helpers import make_year_rules

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.ruleset import YearRules

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
_POSTING = SommaEsentePosting(
    resolver=load_policy_resolver(),
    policy_context=PolicyContext(year=_YEAR, as_of=date(_YEAR, 12, 1)),
    competence_period=CompetencePeriod(year=_YEAR, month=12),
    payment_date=date(_YEAR, 12, 28),
    run_id="2026-12-thirteenth",
)


def _tax(annual: Decimal | None) -> TaxComputation:
    components = (
        ()
        if annual is None
        else (
            TaxLineItem(
                name="somma_esente", amount=annual, rule_id="r", fonte="L. 207/2024"
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
) -> SommaEsenteOutcome:
    return resolve_somma_esente(
        _tax(annual),
        rules,
        opening,
        _position(closed),
        _YEAR,
        _POSTING,
    )


class TestBeforeTheConguaglio:
    """A run before the last slot pays its share, never more than still due."""

    def test_pays_the_slot_share(self) -> None:
        """1,200 EUR over 12 slots: 100.00 per run."""
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

    def test_due_amount_is_provisional_on_the_income_assumed(self) -> None:
        """A due somma esente rests on employment income as reddito complessivo."""
        outcome = _resolve(Decimal(1200), _opening(), closed=0)

        (issue,) = outcome.issues
        assert issue.code == "somma_esente_income_assumed"
        assert issue.status is CalculationStatus.PROVISIONAL


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
