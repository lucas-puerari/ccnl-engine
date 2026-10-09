"""Handler for contract-renewal arrears.

Art. 17 c. 1 lett. b TUIR (text in force until 31 December 2026; art. 19
c. 1 lett. b of the testo unico of D.Lgs. 117/2026 from 2027, see
:mod:`~ccnl_engine.payroll.service.separate_tax_law`) taxes
separately the "emolumenti arretrati per prestazioni di lavoro dipendente
riferibili ad anni precedenti, percepiti per effetto di leggi, di contratti
collettivi, [...] o per altre cause non dipendenti dalla volontà delle
parti"; art. 21 c. 1 sets the rate on half the income of the two years
before the year "in cui sono percepiti", which the caller supplies as
``separate_tax_rate``.  Arrears of the tax year of the run are not
"riferibili ad anni precedenti": they are ordinary employment income of
the year (art. 51 c. 1 TUIR) and enter the IRPEF base of the run.  The
year compared is the tax year of the run, so arrears paid by 12 January
with the December run of the year before belong to that year.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _require_resolution
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.events import ArrearsEvent
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.domain.pay_items import ContractRenewalArrears
from ccnl_engine.payroll.domain.remittance import ARREARS_WITHHOLDING
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service.separate_tax_law import separate_tax_rule
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period_payroll import PeriodId

_CAPABILITY = "contract_renewal_arrears"
#: Reason of arrears of an earlier tax year: separate taxation.
SEPARATE_TAXATION = "separate_taxation"
#: Reason of arrears of the tax year of the run: ordinary IRPEF.
ORDINARY_TAXATION = "ordinary_taxation"
#: Reason of arrears whose reference period is not stated.
REFERENCE_PERIOD_UNKNOWN = "reference_period_unknown"


def _reason(reference: PeriodId | None, tax_year: int, index: str) -> str:
    """Return how the arrears of ``reference`` are taxed in ``tax_year``.

    Returns:
        One of the reasons of this module.

    Raises:
        InvalidInputError: When ``reference`` is after ``tax_year``: arrears
            cannot refer to a year not yet begun.
    """
    if reference is None:
        return REFERENCE_PERIOD_UNKNOWN
    if reference.year > tax_year:
        msg = (
            f"ArrearsEvent {index} refers to {reference.year}-"
            f"{reference.month:02d}, after the tax year {tax_year} of the run"
        )
        raise InvalidInputError(
            msg, field="ArrearsEvent.reference_period", feature=_CAPABILITY
        )
    return SEPARATE_TAXATION if reference.year < tax_year else ORDINARY_TAXATION


def _decision(
    reason: str, event: ArrearsEvent, tax_year: int, amount: Decimal
) -> CalculationDecision:
    reference = event.reference_period
    return CalculationDecision(
        capability=_CAPABILITY,
        status=(
            CalculationStatus.INCOMPLETE
            if reason == REFERENCE_PERIOD_UNKNOWN
            else CalculationStatus.FINAL
        ),
        reason_code=reason,
        rule=separate_tax_rule(tax_year).rule,
        rule_version=str(tax_year),
        inputs={
            "tax_year": str(tax_year),
            "reference_period": (
                "unknown"
                if reference is None
                else f"{reference.year}-{reference.month:02d}"
            ),
            "amount": event.amount,
        },
        amount=amount,
    )


def _unknown_issue(index: str, tax_year: int) -> CalculationIssue:
    law = separate_tax_rule(tax_year)
    return CalculationIssue(
        code="arrears_reference_period_unknown",
        message=(
            f"ArrearsEvent {index} states no reference_period: arrears of an "
            f"earlier year are taxed separately ({law.citation}), "
            "those of the tax year of the run with the ordinary IRPEF; the "
            "run taxes them separately at the caller's rate as a simulation"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact="reference_period",
    )


def _handle_arrears(event: ArrearsEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle contract-renewal arrears.

    Arrears of an earlier tax year, or of an unstated one, are posted to
    CASH_EARNINGS and taxed separately at the caller's rate on
    SEPARATE_TAX; an unstated year also raises a ``missing_fact`` issue.
    Arrears of the tax year of the run are posted to CASH_EARNINGS and
    enter the IRPEF base of the run.

    Returns:
        Handler result with the arrears item, its postings, the INPS base
        it adds and its taxation decision.
    """
    gross = event.amount
    tax_year = ctx.tax_year
    reason = _reason(event.reference_period, tax_year, ctx.evt_id)
    arrears_resolution = _require_resolution(ctx.resolver, _CAPABILITY, ctx.context)
    item = ContractRenewalArrears(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    intents = [
        PostingIntent(
            entry_id=f"cash_{ctx.evt_id}",
            source_item_id=ctx.evt_id,
            pay_item_kind=_CAPABILITY,
            account=AccountKind.CASH_EARNINGS,
            amount=gross,
            policy_decision_id=arrears_resolution.policy_id,
        )
    ]
    if reason == ORDINARY_TAXATION:
        return EventEffect(
            items=[item],
            intents=intents,
            inps_delta=gross,
            irpef_delta=gross,
            decisions=[_decision(reason, event, tax_year, gross)],
        )
    sep_tax = money(gross * event.separate_tax_rate)
    intents.append(
        PostingIntent(
            entry_id=f"sep_tax_{ctx.evt_id}",
            source_item_id=ctx.evt_id,
            pay_item_kind=_CAPABILITY,
            account=AccountKind.SEPARATE_TAX,
            amount=sep_tax,
            policy_decision_id=arrears_resolution.policy_id,
            remittance_code=ARREARS_WITHHOLDING,
        )
    )
    unknown = reason == REFERENCE_PERIOD_UNKNOWN
    return EventEffect(
        items=[item],
        intents=intents,
        inps_delta=gross,
        decisions=[_decision(reason, event, tax_year, sep_tax)],
        issues=[_unknown_issue(ctx.evt_id, tax_year)] if unknown else [],
    )
