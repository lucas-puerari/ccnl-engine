"""Elemento di Raccordo Contrattuale the CCNL pays with the tredicesima.

Renewal of the CCNL grafici editoriali of 19 January 2021: the ERC is
"congelato in cifra fissa non rivalutabile e non assorbibile, è
omnicomprensivo e pertanto non avrà alcuna incidenza su alcun istituto
contrattuale o di legge, e dall'anno 2021 maturerà progressivamente per
mese/frazione di mese e verrà corrisposto [...] nel mese di dicembre
contestualmente alla gratifica natalizia".  The run that pays the rateo of
the tredicesima, or liquidates it at the termination, pays the ERC of the
same months: ``Employment.erc_amount`` x months / 12.  It is ordinary pay
for IRPEF and INPS and stays out of the TFR base
(``raccordo_element_earning``, policy ``it/earning/raccordo_element``).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.payroll.application.period._run_decisions import _ccnl_rule
from ccnl_engine.payroll.application.year._extra_month_settlement import (
    ExtraMonthSettlement,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.extra_month_schedule import ExtraMonthKind
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import RaccordoElementEarning
from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._rule_lookup import Rule

__all__ = ["ERC_UNKNOWN", "erc_decisions", "erc_rules", "erc_settlement"]

_ZERO = Decimal(0)
_TWELVE = Decimal(12)
_KIND = "raccordo_element_earning"
#: The ERC of a run that pays it needs the employment to state it.
ERC_UNKNOWN = CalculationIssue(
    code="erc_unknown",
    message=(
        "the CCNL pays the Elemento di Raccordo Contrattuale with the "
        "tredicesima and the employment does not state it: the amounts shown "
        "leave it out; state Employment.erc_amount"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="erc_amount",
)


def _months(ctx: RunContext) -> int:
    """Return the months of tredicesima the run pays or liquidates.

    Returns:
        Zero when the CCNL pays no ERC or the run pays no tredicesima.
    """
    if ctx.contract.ccnl.parameters.raccordo_element is None:
        return 0
    own = () if ctx.accrual is None else (ctx.accrual,)
    return sum(
        a.months for a in own + ctx.settlements if a.kind is ExtraMonthKind.THIRTEENTH
    )


def _amount(ctx: RunContext) -> Decimal | None:
    """Return the ERC of the run, ``None`` when the employment omits it.

    Returns:
        The annual ERC x months / 12, rounded to the cent.
    """
    annual = ctx.request.erc_amount
    if annual is None:
        return None
    return money(annual * Decimal(_months(ctx)) / _TWELVE)


def erc_settlement(ctx: RunContext) -> ExtraMonthSettlement:
    """Return the ERC paid on the run, with the bases it enters.

    Returns:
        Its earning and ledger entry; the ``erc_unknown`` issue when the
        run pays a tredicesima of a CCNL with an ERC the employment does
        not state; nothing otherwise.
    """
    if _months(ctx) == 0:
        return ExtraMonthSettlement()
    amount = _amount(ctx)
    if amount is None:
        return ExtraMonthSettlement(issues=(ERC_UNKNOWN,))
    if amount == _ZERO:
        return ExtraMonthSettlement()
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    payment = ctx.contract.tctx.payment
    item_id = f"erc_{ctx.run_id}"
    item = RaccordoElementEarning(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=amount,
        source=f"Elemento di Raccordo Contrattuale: {_months(ctx)}/12",
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


def erc_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Return the ``base_salary`` decision of the ERC the run pays.

    Returns:
        One decision with reason ``erc_paid``, provisional with reason
        ``required_fact_missing`` when the ERC is not stated; none when the
        run pays no ERC.
    """
    clause = ctx.contract.ccnl.parameters.raccordo_element
    months = _months(ctx)
    if clause is None or months == 0:
        return ()
    rule, version = _ccnl_rule(ctx.contract.ccnl, ctx.contract.tctx.competence.year)
    amount = _amount(ctx)
    annual = ctx.request.erc_amount
    inputs: dict[str, Decimal | str] = {"months": str(months)}
    if annual is not None:
        inputs["annual"] = annual
    return (
        CalculationDecision(
            capability="base_salary",
            status=(
                CalculationStatus.FINAL
                if amount is not None
                else CalculationStatus.PROVISIONAL
            ),
            reason_code="erc_paid" if amount is not None else "required_fact_missing",
            rule=f"{rule}:raccordo_element",
            rule_version=version,
            inputs=inputs,
            source=clause.provenance.location,
            amount=amount,
        ),
    )


def erc_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the ERC clause when the run pays the ERC.

    Returns:
        The clause of the CCNL, empty when the run pays none.
    """
    clause = ctx.contract.ccnl.parameters.raccordo_element
    if clause is None or _months(ctx) == 0:
        return ()
    rule = _ccnl_rule(ctx.contract.ccnl, ctx.contract.tctx.competence.year)[0]
    return ((f"{rule}:raccordo_element", clause.provenance),)
