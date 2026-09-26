"""Somma esente of a run: share, conguaglio and recovery (L. 207/2024 art. 1)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._somma_esente import (
    SommaEsenteOutcome,
    SommaEsentePosting,
    resolve_somma_esente,
)
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.obligations import (
    SOMMA_ESENTE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.period import PeriodState
from ccnl_engine.payroll.domain.policy import PolicyContext
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.domain.tax import TaxComputation, TaxLineItem
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import SommaEsenteAccount
from ccnl_engine.payroll.service.policy_loader import load_policy_resolver
from ccnl_engine.tax.domain.credit_rules import SommaEsenteBand, SommaEsenteRules
from tests.helpers import make_year_rules

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.ruleset import YearRules

_ZERO = Decimal(0)
_YEAR = 2026
# 12 slots, one per regular month.
_SCHEDULE = WithholdingSchedule.from_calendar(WorkCalendar(year=_YEAR))
_SLOTS = _SCHEDULE.run_count.value
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
    closed: int,
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
        ytd=TaxYearState(
            tax_year=_YEAR,
            regular_periods_closed=min(closed, 12),
            tax_withholding_periods_closed=closed,
            somma_esente=SommaEsenteAccount(recognized=recognized, recovered=recovered),
        ),
        obligations=obligations,
    )


def _resolve(
    annual: Decimal | None, opening: PeriodState, rules: YearRules = _RULES
) -> SommaEsenteOutcome:
    return resolve_somma_esente(
        _tax(annual),
        rules,
        opening,
        _SCHEDULE,
        _YEAR,
        _POSTING,
    )


class TestBeforeTheConguaglio:
    """A run before the last slot pays its share, never more than still due."""

    def test_pays_the_slot_share(self) -> None:
        """1,200 EUR over 12 slots: 100.00 per run."""
        outcome = _resolve(Decimal(1200), _opening(closed=0))

        assert outcome.amount == Decimal("100.00")
        assert outcome.due == Decimal("1200.00")
        assert outcome.reason == "share_paid"
        assert outcome.items[0].item_id == "somma_esente_2026-12-thirteenth"
        assert outcome.entries[0].amount == Decimal("100.00")

    def test_caps_the_share_at_what_is_still_due(self) -> None:
        """1,150 paid of 1,200 due: the run pays the 50 left, not 100."""
        outcome = _resolve(Decimal(1200), _opening(closed=5, recognized=Decimal(1150)))

        assert outcome.amount == Decimal(50)

    def test_holds_an_excess_until_the_conguaglio(self) -> None:
        """The due fell below what was paid: nothing paid, nothing recovered."""
        outcome = _resolve(Decimal(300), _opening(closed=6, recognized=Decimal(600)))

        assert outcome.amount == _ZERO
        assert outcome.reason == "overpayment_pending_conguaglio"
        assert outcome.items == ()
        assert outcome.decisions[0].inputs["net_paid_before"] == Decimal(600)

    def test_not_due_on_income_above_the_bands(self) -> None:
        """No component: zero, with a decision saying so."""
        outcome = _resolve(None, _opening(closed=0))

        assert outcome.amount == _ZERO
        assert outcome.due == _ZERO
        assert outcome.reason == "not_due"
        assert outcome.decisions[0].capability == "somma_esente"
        assert outcome.issues == ()

    def test_due_amount_is_provisional_on_the_income_assumed(self) -> None:
        """A due somma esente rests on employment income as reddito complessivo."""
        outcome = _resolve(Decimal(1200), _opening(closed=0))

        (issue,) = outcome.issues
        assert issue.code == "somma_esente_income_assumed"
        assert issue.status is CalculationStatus.PROVISIONAL


class TestAtTheConguaglio:
    """The last slot settles the balance and recovers an over-payment."""

    def test_pays_the_balance(self) -> None:
        """The last slot pays exactly the due not yet paid, cents included."""
        outcome = _resolve(
            Decimal("877.04064"),
            _opening(closed=_SLOTS - 1, recognized=Decimal("809.52")),
        )

        assert outcome.amount == Decimal("67.52")
        assert outcome.reason == "settled_at_conguaglio"

    def test_recovers_up_to_60_eur_in_full(self) -> None:
        """40 EUR paid in excess are recovered on the conguaglio payslip."""
        outcome = _resolve(
            Decimal(500), _opening(closed=_SLOTS - 1, recognized=Decimal(540))
        )

        assert outcome.amount == Decimal(-40)
        assert outcome.reason == "overpayment_recovered"
        assert outcome.plan is None
        assert outcome.items[0].item_id == "somma_esente_recovery_2026-12-thirteenth"
        assert outcome.entries[0].amount == Decimal(-40)

    def test_recovers_above_60_eur_in_ten_installments(self) -> None:
        """150 EUR in excess: 15 EUR now, nine installments left."""
        outcome = _resolve(
            Decimal(500), _opening(closed=_SLOTS - 1, recognized=Decimal(650))
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
            _opening(closed=_SLOTS - 1, recognized=Decimal(540), recovered=Decimal(40)),
        )

        assert outcome.amount == _ZERO
        assert outcome.reason == "settled_at_conguaglio"


class TestRunningRecovery:
    """A plan of the current year posts its installment on every later run."""

    _PLAN = RecoveryPlan.create(SOMMA_ESENTE_RECOVERY, Decimal(150), 10)

    def test_posts_the_next_installment(self) -> None:
        """The plan, not the projection, sets the amount."""
        plan = self._PLAN.advance()
        outcome = _resolve(Decimal(500), _opening(closed=_SLOTS, plan=plan))

        assert outcome.amount == Decimal("-15.00")
        assert outcome.reason == "installment_posted"
        assert outcome.plan == plan.advance()
        assert outcome.decisions[0].inputs["recovery_in_progress"] == "true"

    def test_last_installment_closes_the_plan(self) -> None:
        """After the last installment no plan is left."""
        plan = replace(self._PLAN, installments_posted=9)
        outcome = _resolve(Decimal(500), _opening(closed=_SLOTS, plan=plan))

        assert outcome.amount == Decimal("-15.00")
        assert outcome.reason == "last_installment_posted"
        assert outcome.plan is None


class TestNotInForce:
    """Without rules and nothing paid there is nothing to decide."""

    def test_returns_an_empty_outcome(self) -> None:
        """No amount, no posting, no decision."""
        rules = _RULES.model_copy(update={"somma_esente": None})

        assert _resolve(None, _opening(closed=0), rules) == SommaEsenteOutcome()

    def test_still_settles_what_was_paid(self) -> None:
        """Credit paid under rules no longer in force is recovered at conguaglio."""
        rules = _RULES.model_copy(update={"somma_esente": None})
        outcome = _resolve(
            None, _opening(closed=_SLOTS - 1, recognized=Decimal(30)), rules
        )

        assert outcome.amount == Decimal(-30)
        assert outcome.reason == "overpayment_recovered"
