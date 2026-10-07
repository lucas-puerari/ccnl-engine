"""INPS contributions and TFR accrual of one run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.amounts._domestic import (
    compute_domestic_breakdown,
)
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service._contributions_rates import resolve_rates
from ccnl_engine.payroll.service.contributions import resolve_contributions

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown


def _ordinary_breakdown(inp: _AmountsInput, base: Decimal) -> ContributionBreakdown:
    """Return the ordinary INPS breakdown of ``base`` for the run.

    Returns:
        The breakdown with the YTD INPS base and the IVS ceiling of the run.
    """
    return resolve_contributions(
        base,
        inp.rules,
        inp.contract_type,
        inp.category,
        ytd_inps_base=inp.ytd_inps_base,
        ivs_ceiling_applies=inp.ivs_ceiling_applies,
    )


def run_contributions(inp: _AmountsInput) -> tuple[ContributionBreakdown, Decimal]:
    """Return the INPS breakdown of the run and the employee rate for IRPEF.

    Domestic CCNLs have no ordinary INPS rules: their flat per-hour
    contributions apply and no employee rate is projected on the slots
    still to come.

    Returns:
        ``(breakdown, employee_rate)``.
    """
    period_inps_base = inp.monthly_gross + inp.event_inps_base
    if inp.rules.inps is not None:
        breakdown = _ordinary_breakdown(inp, period_inps_base)
        rates = resolve_rates(inp.rules, inp.contract_type, inp.category)
        return breakdown, rates.employee_rate
    breakdown = compute_domestic_breakdown(
        inp.rules,
        inp.weekly_hours,
        inp.contributable_hours,
        inp.domestic_hourly_rate,
        inp.contract_type,
    )
    return breakdown, _ZERO


def recurring_employee_inps(inp: _AmountsInput, inps_employee: Decimal) -> Decimal:
    """Return the employee INPS of the recurring pay of the run alone.

    Returns:
        ``inps_employee`` for domestic CCNLs, else the employee INPS of the
        monthly gross without the events.
    """
    return (
        inps_employee
        if inp.rules.inps is None
        else _ordinary_breakdown(inp, inp.monthly_gross).employee
    )


#: Code of the issue of an apprentice TFR whose deduction is undetermined.
TFR_APPRENTICE_IVS_CODE = "tfr_apprentice_additional_ivs_undetermined"


@dataclass(frozen=True)
class TfrAccrual:
    """The TFR of one run: the art. 2120 c.c. quota less the additional IVS.

    Attributes:
        quota: TFR base of the run over the accrual divisor, rounded.
        ivs_base: Employer IVS base of the run the additional IVS is
            charged on, zero when no deduction applies.
        ivs_rate: Additional IVS rate of L. 297/1982 art. 3 c. 15, zero
            when no deduction applies.
        deduction: Additional IVS deducted from the quota under c. 16,
            never above the quota.
        undetermined: The sector deducts the additional IVS but the worker
            is an apprentice, whose overall contribution rate (L. 296/2006
            art. 1 c. 773) no bundled source splits: the quota accrues
            whole and the TFR is provisional.
    """

    quota: Decimal
    ivs_base: Decimal = _ZERO
    ivs_rate: Decimal = _ZERO
    deduction: Decimal = _ZERO
    undetermined: bool = False

    @property
    def amount(self) -> Decimal:
        """TFR accrued on the run, to the company or to the pension fund."""
        return self.quota - self.deduction

    @property
    def status(self) -> CalculationStatus:
        """Provisional when the deduction of an apprentice is undetermined."""
        if self.undetermined:
            return CalculationStatus.PROVISIONAL
        return CalculationStatus.FINAL

    def issues(self) -> tuple[CalculationIssue, ...]:
        """Return the issue of an undetermined apprentice deduction.

        Returns:
            One provisional issue, or nothing when the TFR is final.
        """
        if not self.undetermined:
            return ()
        return (
            CalculationIssue(
                code=TFR_APPRENTICE_IVS_CODE,
                message=(
                    "tfr: whether the 0.50% additional IVS of L. 297/1982 "
                    "art. 3 cc. 15-16 is due on an apprentice, whose overall "
                    "rate is set by L. 296/2006 art. 1 c. 773, is not sourced; "
                    "the TFR quota accrues whole, without the deduction"
                ),
                status=CalculationStatus.PROVISIONAL,
            ),
        )


def _ivs_employer_base(breakdown: ContributionBreakdown) -> Decimal:
    """Return the employer IVS base of the run, zero without an IVS share.

    Returns:
        The base of the ``ivs_employer`` component, capped at the
        massimale when it applies.
    """
    return next(
        (c.base for c in breakdown.components if c.name == "ivs_employer"), _ZERO
    )


def tfr_accrual(inp: _AmountsInput, breakdown: ContributionBreakdown) -> TfrAccrual:
    """Return the TFR accrued on the run.

    L. 297/1982 art. 3 c. 16: the employer deducts from the TFR quota of
    the period the 0.50% additional IVS contribution of c. 15, charged on
    the IVS base of the same period; when the TFR goes to a pension fund
    the deduction reduces the TFR paid to it.  A quota smaller than the
    contribution is deducted down to zero.  Sectors with no additional
    IVS rule accrue the whole quota; so do apprentices, provisionally.

    Returns:
        The quota over the accrual divisor and the deduction taken from it.
    """
    tfr = inp.rules.tfr
    quota = money((inp.monthly_gross + inp.event_tfr_base) / tfr.accrual_divisor)
    extra = tfr.additional_ivs
    if extra is None:
        return TfrAccrual(quota=quota)
    if isinstance(inp.contract_type, Apprentice):
        return TfrAccrual(quota=quota, undetermined=True)
    base = _ivs_employer_base(breakdown)
    deduction = min(quota, money(base * extra.rate))
    return TfrAccrual(
        quota=quota, ivs_base=base, ivs_rate=extra.rate, deduction=deduction
    )
