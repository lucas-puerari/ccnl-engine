"""Elemento perequativo the CCNL pays where no second-level bargaining exists.

CCNL metalmeccanici Federmeccanica of 5 February 2021, art. 13 (Sez.
Quarta, Titolo IV): the workers "in forza al 1° gennaio di ogni anno nelle
aziende prive di contrattazione di secondo livello" on pay are paid, "con la
retribuzione del mese di giugno, una cifra annua pari a 260 euro" (485 from
2014), "ovvero una cifra inferiore fino a concorrenza in caso di presenza di
retribuzioni aggiuntive a quelle fissate dal CCNL, in funzione della durata,
anche non consecutiva, del rapporto di lavoro nel corso dell'anno
precedente"; a fraction of a month above 15 days counts as a whole month.

The run pays ``annual_amount`` x the months of the employment in the year
before / 12, rounded to the cent, less
``PriorYearTaxFacts.pay_above_ccnl``, never below zero.  The months count
the duration of the employment, not the presence: absences do not reduce
them.  The run that pays it is the regular run of ``payment_month``, or,
when the employment ends earlier in the year, the run that pays the
termination month ("all'atto della liquidazione delle competenze").  It is
ordinary pay for IRPEF and INPS of the year paid, outside the TFR base
(``perequativo_element_earning``, policy ``it/earning/perequativo_element``)
and outside the extra months, whose base is the pay chain.

Two facts decide it.  ``EmployerProfile.second_level_bargaining`` left
``None`` leaves the element out with a ``missing_fact`` blocker
(:func:`ccnl_engine.employment.fact.services.bargaining_issue`);
``PriorYearTaxFacts.pay_above_ccnl`` left ``None`` leaves it out with the
issue :data:`PAY_ABOVE_CCNL_UNKNOWN`.  The text does not scale the amount
for a part-time worker: the run pays it in full and traverses the
limitation ``elemento_perequativo_part_time`` of the CCNL.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.decision.rules import _ccnl_rule
from ccnl_engine.extra_month.liquidation.services import pays_month
from ccnl_engine.extra_month.models import MonthAccrualRule
from ccnl_engine.extra_month.schedule.models import AccrualWindow
from ccnl_engine.extra_month.settlement.services import ExtraMonthSettlement
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.facade import PerequativoElementEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.run.models import PayrollRun, run_identifier

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.capability.rule.services import Rule
    from ccnl_engine.compensation.models import PerequativoElement
    from ccnl_engine.employment.fact.inputs import EmploymentPeriod
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.period.requests import PeriodCalculationRequest

__all__ = [
    "PART_TIME_VARIANT",
    "PAY_ABOVE_CCNL_UNKNOWN",
    "perequativo_decisions",
    "perequativo_months",
    "perequativo_paths",
    "perequativo_rules",
    "perequativo_settlement",
]

_ZERO = Decimal(0)
_TWELVE = 12
_KIND = "perequativo_element_earning"
#: Variant of the CCNL note on the part-time worker, whom the text does not
#: name.
PART_TIME_VARIANT = "elemento_perequativo_part_time"
#: The element a run pays needs the pay above the CCNL of the year before.
PAY_ABOVE_CCNL_UNKNOWN = CalculationIssue(
    code="pay_above_ccnl_unknown",
    message=(
        "the CCNL pays the elemento perequativo less the pay above the CCNL "
        "the worker received in the year before, and the request does not "
        "state it: the amounts shown leave the element out; state "
        "PriorYearTaxFacts.pay_above_ccnl (zero when the worker received "
        "only the pay the CCNL fixes)"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="pay_above_ccnl",
)


def perequativo_months(request: PeriodCalculationRequest, ccnl: CCNL) -> int:
    """Return the months of the year before the run pays the element for.

    Whether the employer has second-level bargaining is not read here.

    Args:
        request: The period request.
        ccnl: The contract.

    Returns:
        The qualifying months of the year before, 12 when the employment
        period is not stated; zero when the CCNL has no element, the run
        does not pay the month that carries it, or the worker was not in
        force on 1 January.
    """
    clause = ccnl.parameters.perequativo_element
    if clause is None:
        return 0
    period, month = request.employment_period, request.period_id
    target = _paying_month(clause, period, month.year)
    run_id = run_identifier(request.run, month.year, month.month)
    regular = PayrollRun.regular(month.year, target).identifier
    if run_id.month != target or not pays_month(request, run_id, regular):
        return 0
    if period is None:
        return _TWELVE
    return _previous_year_months(clause, period, month.year)


def _paying_month(
    clause: PerequativoElement, period: EmploymentPeriod | None, year: int
) -> int:
    """Return the month whose run pays the element of ``year``.

    Returns:
        The termination month when the employment ends in ``year`` before
        the payment month, else the payment month.
    """
    ended_on = None if period is None else period.ended_on
    if ended_on is not None and ended_on.year == year:
        return min(ended_on.month, clause.payment_month)
    return clause.payment_month


def _previous_year_months(
    clause: PerequativoElement, period: EmploymentPeriod, year: int
) -> int:
    """Return the months of employment in the year before ``year``.

    Returns:
        The months of the year before that pass the month rule of the
        clause; zero for an employment started after its last day, not in
        force on 1 January of ``year``.
    """
    first, last = date(year - 1, 1, 1), date(year - 1, 12, 31)
    if period.started_on > last:
        return 0
    stored = clause.month_rule
    rule = MonthAccrualRule(
        min_days=stored.min_days,
        comparison=stored.comparison,
        working_days=stored.working_days,
        source="CCNL elemento perequativo",
        provenance=stored.provenance,
    )
    window = AccrualWindow(
        nominal_start=first, start=max(first, period.started_on), end=last
    )
    return rule.qualifying_months(window)


@dataclass(frozen=True)
class _Owed:
    """The element a run owes before the pay above the CCNL is known.

    Attributes:
        clause: The clause of the CCNL.
        months: Qualifying months of the year before.
        annual: The yearly amount in force on 1 January.
        prorated: ``annual`` x ``months`` / 12, rounded to the cent.
        above: Pay above the CCNL of the year before, ``None`` when unknown.
    """

    clause: PerequativoElement
    months: int
    annual: Decimal
    prorated: Decimal
    above: Decimal | None

    @property
    def amount(self) -> Decimal | None:
        """The amount paid, ``None`` when the pay above the CCNL is unknown."""
        if self.above is None:
            return None
        return max(self.prorated - self.above, _ZERO)


def _owed(ctx: RunContext) -> _Owed | None:
    """Return the element the run owes to a worker without bargaining.

    Returns:
        ``None`` when the run pays no element or the employer has or may
        have second-level bargaining.
    """
    clause = ctx.contract.ccnl.parameters.perequativo_element
    if clause is None or ctx.request.employer.second_level_bargaining is not False:
        return None
    months = perequativo_months(ctx.request, ctx.contract.ccnl)
    if months == 0:
        return None
    annual = clause.annual_amount.value_at(date(ctx.request.period_id.year, 1, 1))
    prorated = money(annual * Decimal(months) / Decimal(_TWELVE))
    above = ctx.request.prior_year.pay_above_ccnl
    return _Owed(clause, months, annual, prorated, above)


def perequativo_settlement(ctx: RunContext) -> ExtraMonthSettlement:
    """Return the elemento perequativo paid on the run, with its bases.

    Returns:
        Its earning and ledger entry; the ``pay_above_ccnl_unknown`` issue
        when the run owes it and the pay above the CCNL is not stated;
        nothing when the run owes none or the pay above absorbs it.
    """
    owed = _owed(ctx)
    if owed is None:
        return ExtraMonthSettlement()
    amount = owed.amount
    if amount is None:
        return ExtraMonthSettlement(issues=(PAY_ABOVE_CCNL_UNKNOWN,))
    if amount == _ZERO:
        return ExtraMonthSettlement()
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    payment = ctx.contract.tctx.payment
    item_id = f"perequativo_{ctx.run_id}"
    item = PerequativoElementEarning(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(1),
        amount=amount,
        source=f"Elemento perequativo: {owed.months}/12",
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


def perequativo_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Return the ``base_salary`` decision of the element the run owes.

    Returns:
        One decision with reason ``perequativo_paid`` (amount zero when the
        pay above the CCNL absorbs it), provisional with reason
        ``required_fact_missing`` when that pay is not stated; none when
        the run owes no element or the bargaining is not stated.
    """
    owed = _owed(ctx)
    if owed is None:
        return ()
    rule, version = _ccnl_rule(ctx.contract.ccnl, ctx.contract.tctx.competence.year)
    amount = owed.amount
    inputs: dict[str, Decimal | str] = {
        "months": str(owed.months),
        "annual": owed.annual,
        "prorated": owed.prorated,
    }
    if owed.above is not None:
        inputs["pay_above_ccnl"] = owed.above
    known = amount is not None
    return (
        CalculationDecision(
            capability="base_salary",
            status=CalculationStatus.FINAL if known else CalculationStatus.PROVISIONAL,
            reason_code="perequativo_paid" if known else "required_fact_missing",
            rule=f"{rule}:perequativo_element",
            rule_version=version,
            inputs=inputs,
            source=owed.clause.provenance.location,
            amount=amount,
        ),
    )


def perequativo_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the clause of the element when the run owes it.

    Returns:
        The clause of the CCNL, empty when the run owes none.
    """
    owed = _owed(ctx)
    if owed is None:
        return ()
    rule = _ccnl_rule(ctx.contract.ccnl, ctx.contract.tctx.competence.year)[0]
    return ((f"{rule}:perequativo_element", owed.clause.provenance),)


def perequativo_paths(ctx: RunContext) -> frozenset[str]:
    """Return the limitation path of the element paid to a part-time worker.

    Returns:
        ``<ccnl id>/elemento_perequativo_part_time`` when the run pays the
        element to a worker whose weekly hours are below the full time;
        nothing otherwise.
    """
    owed = _owed(ctx)
    hours, full = ctx.request.weekly_hours, ctx.request.full_time_weekly_hours
    paid = owed is not None and bool(owed.amount)
    if not paid or hours is None or full is None or hours.value >= full.value:
        return frozenset()
    return frozenset({f"{ctx.contract.ccnl.meta.ccnl_id}/{PART_TIME_VARIANT}"})
