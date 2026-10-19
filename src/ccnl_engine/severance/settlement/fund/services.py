"""The fund a termination settles: its parts, its destination and its revaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationStatus,
)
from ccnl_engine.employment.fact.inputs import PublicEndOfService
from ccnl_engine.run.models import RunKind
from ccnl_engine.severance.provision.services import tfr_treasury_fund
from ccnl_engine.severance.revaluation.services import run_tfr_revaluation
from ccnl_engine.severance.settlement.gap.models import (
    _PENSION_FUND,
    _TFR_AT_INPS,
    _TREASURY,
    _TREASURY_UNKNOWN,
    _Gap,
)

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.severance.settlement.models import TfrSettlementRules

#: Capability of the TFR settlement, as the events name it.
CAPABILITY = "termination_tfr"
_KIND = "tfr_settlement_item"
_ZERO = Decimal(0)
_MONTHS = 12
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
#: Months of service up to which a fixed term takes the art. 19 c. 1-ter deduction.
_SHORT_FIXED_TERM = 24
_FINAL = CalculationStatus.FINAL
_INCOMPLETE = CalculationStatus.INCOMPLETE


@dataclass(frozen=True)
class _Fund:
    """The fund at 31 December of the year before and what it holds."""

    amount: Decimal
    revaluations: Decimal | None
    advances: Decimal | None


def _destination_gap(ctx: RunContext, run_to_pension_fund: bool) -> _Gap | None:
    """Return why the employer does not pay the TFR, ``None`` when it does.

    Returns:
        The gap of a TFR at INPS, at the Fondo Tesoreria (or not known to
        be out of it) or at a pension fund.
    """
    if ctx.request.public_end_of_service in _AT_INPS:
        return _TFR_AT_INPS
    if run_to_pension_fund:
        return _PENSION_FUND
    treasury = tfr_treasury_fund(ctx)
    if treasury is None:
        return _TREASURY_UNKNOWN
    return _TREASURY if treasury else None


def _fund(ctx: RunContext, year: int, started_on: date) -> _Fund | None:
    """Return the fund at 31 December of ``year - 1``, ``None`` when unknown.

    An employment that starts in ``year`` without a stated fund has none;
    one that carries a TFR over (art. 2112 c.c.) states it.

    Returns:
        The stated fund of ``year - 1``; an empty fund for an employment
        of ``year`` that states none; ``None`` otherwise.
    """
    stated = ctx.request.tfr_fund
    if stated is None:
        return _Fund(_ZERO, _ZERO, _ZERO) if started_on.year == year else None
    if stated.year != year - 1:
        return None
    return _Fund(stated.amount, stated.revaluations, stated.advances)


def _quotas_before(ctx: RunContext, started_on: date) -> Decimal | None:
    """Return the TFR the earlier runs of the year accrued with the employer.

    Returns:
        The quotas of the competence year of the run in the opening state,
        ``None`` when they are not known or a regular month of the year
        the worker was employed in before the run is not closed.
    """
    accrual = ctx.opening.accrual
    year, month = ctx.cp.year, ctx.request.period_id.month
    quota = accrual.tfr_quota(year)
    first = 1 if started_on.year < year else started_on.month
    closed = {r.month for r in accrual.runs_of(year) if r.kind is RunKind.REGULAR}
    if quota is None or not set(range(first, month)) <= closed:
        return None
    return quota.amount


def _revaluation(ctx: RunContext, fund: _Fund) -> Decimal | None:
    """Return the revaluation of the year net of its tax, ``None`` if unknown.

    Returns:
        Zero for an empty fund; the revaluation the run decides less its
        substitute tax; ``None`` when the run does not compute it.
    """
    if not fund.amount:
        return _ZERO
    revaluation = run_tfr_revaluation(ctx)
    return None if revaluation is None else revaluation.net


def _rules_of(ctx: RunContext, year: int) -> TfrSettlementRules | None:
    """Return the settlement rules of a termination in ``year``.

    Returns:
        The rules of the tax year of the run when it is ``year``; ``None``
        when the run is paid in another tax year (art. 19 c. 1 TUIR takes
        the brackets of the termination year) or the year has none.
    """
    rules = ctx.contract.year_rules
    return rules.tfr_settlement if rules.year == year else None
