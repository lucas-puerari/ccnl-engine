"""Reduction of the gross of a public employee under the TFR at INPS.

DPCM 20 dicembre 1999 art. 1: under the TFR the 2.50% contribution of the
TFS is suppressed (c. 2) and "la retribuzione lorda viene ridotta in misura
pari al contributo previdenziale obbligatorio soppresso e contestualmente
viene stabilito un recupero in misura pari alla riduzione attraverso un
corrispondente incremento figurativo ai fini previdenziali e
dell'applicazione delle norme sul trattamento di fine rapporto" (c. 3).
The run posts the reduction as a negative earning (``public_tfr_reduction``,
policy ``it/deduction/public_tfr_reduction``): it lowers the gross, the
cost of the administration and the IRPEF taxable, and stays out of the
INPS and TFR bases, which keep the unreduced pay.

It also rejects the regimes a public employee cannot have: the TFS is the
regime of a worker employed before 2001 who did not opt, so a fixed term
or an enrolment in Perseo Sirio or Espero, which the option conditions, is
on the TFR (Schede 'I destinatari e i contributi': "Assunti dopo il
31-dic-2000 ovvero a tempo determinato" and "Assunti prima del 1-gen-2001
(optanti)").
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.accrual.services_extra_month_settlement import (
    ExtraMonthSettlement,
)
from ccnl_engine.payroll.amount.facade import PublicTfrReduction
from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.contribution.inputs_pension_fund import PensionFundEnrolment
from ccnl_engine.payroll.contribution.services_public_end_of_service import (
    end_of_service_base,
)
from ccnl_engine.payroll.employment.inputs import FixedTerm
from ccnl_engine.payroll.employment.inputs_fact import PublicEndOfService
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.models_run import RunKind
from ccnl_engine.payroll.period.services_shared import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.event.handlers_totals import _EventTotals
    from ccnl_engine.payroll.period.services_run_context import RunContext

__all__ = ["public_tfr_reduction"]

_ZERO = Decimal(0)
_KIND = "public_tfr_reduction"
_EXTRA = frozenset({RunKind.THIRTEENTH, RunKind.FOURTEENTH})
_FIELD = "Employment.public_end_of_service"


def _check_regime(ctx: RunContext) -> None:
    """Reject a regime the employment cannot have.

    Raises:
        InvalidInputError: When the regime is stated outside the public
            administrations, or is the TFS of a fixed term or of a worker
            enrolled in a pension fund.
    """
    request = ctx.request
    regime = request.public_end_of_service
    if regime is None:
        return
    if ctx.contract.ccnl.meta.tax_sector is not TaxSector.PUBBLICA_AMMINISTRAZIONE:
        msg = f"{_FIELD} is for the employees of the public administrations"
        raise InvalidInputError(msg, field=_FIELD, feature="inps_employee")
    fixed = isinstance(request.contract_type, FixedTerm)
    enrolled = isinstance(request.pension_fund, PensionFundEnrolment)
    if regime is PublicEndOfService.TFS and (fixed or enrolled):
        msg = (
            f"{_FIELD} is tfs, but a fixed term or a worker enrolled in a "
            "pension fund is on the TFR (DPCM 20 dicembre 1999)"
        )
        raise InvalidInputError(msg, field=_FIELD, feature="inps_employee")


def public_tfr_reduction(ctx: RunContext, totals: _EventTotals) -> ExtraMonthSettlement:
    """Return the reduction of the gross the run posts, if any.

    Returns:
        A negative earning of 2.50% of the end-of-service base under the TFR
        at INPS; nothing otherwise.
    """
    _check_regime(ctx)
    regime = ctx.request.public_end_of_service
    inps = ctx.contract.year_rules.inps
    rates = None if inps is None else inps.end_of_service
    pay = ctx.tfr_pay + totals.tfr_base
    extra = ctx.run_kind in _EXTRA
    base = end_of_service_base(rates, regime, pay, extra=extra)
    if rates is None or base is None or regime is not PublicEndOfService.TFR_INPS:
        return ExtraMonthSettlement()
    amount = -money(base * rates.tfs_employee_rate)
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    payment = ctx.contract.tctx.payment
    item_id = f"public_tfr_reduction_{ctx.run_id}"
    item = PublicTfrReduction(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=amount,
        source="DPCM 20 dicembre 1999 art. 1 c. 3",
    )
    entry = _make_entry(
        item_id,
        item_id,
        _KIND,
        ctx.cp,
        payment,
        AccountKind.CASH_EARNINGS,
        amount,
        policy_id=resolution.policy_id,
    )
    return ExtraMonthSettlement(
        items=(item,),
        entries=(entry,),
        inps_base=amount if treatment.inps else _ZERO,
        tfr_base=amount if treatment.tfr else _ZERO,
        irpef_base=amount if treatment.irpef else _ZERO,
    )
