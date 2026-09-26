"""Opening balances imported from a previous payroll provider.

An integration that takes over an employment mid-year, or at the start of
a year with a recovery still running, states the progressive totals of the
previous provider here.  :meth:`OpeningBalances.to_state` validates them
and returns the :class:`~ccnl_engine.payroll.domain.period.PeriodState` to
pass as ``opening_state`` to the first run computed by the engine.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from decimal import Decimal
from typing import final

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    SommaEsenteAccount,
    TaxYtd,
    TrattamentoAccount,
    UlterioreDetrazioneAccount,
    WithholdingShortfall,
)

__all__ = ["OpeningBalances"]

_ZERO = Decimal(0)
_CENT = Decimal("0.01")
_FEATURE = "opening_balances"


@final
@dataclass(frozen=True)
class OpeningBalances:
    """Progressive totals of a tax year computed outside the engine.

    Every amount is in EUR, non-negative and with at most two decimals; an
    amount left ``None`` (a ``*_due``) is not known.
    The totals are validated by the same rules as the state the engine
    produces (:class:`~ccnl_engine.payroll.domain.tax_year_state.TaxYearState`
    and its accounts); a violation is raised as ``InvalidInputError``.

    Attributes:
        tax_year: Tax year of the totals.
        regular_periods_closed: Regular runs already paid this tax year.
        tax_withholding_periods_closed: Runs that already consumed an IRPEF
            withholding slot this tax year (regular and extra months).
        closed_run_ids: Identifiers of the runs already paid, in payment
            order, when the integration keeps them
            (:meth:`~ccnl_engine.payroll.domain.run.PayrollRunId.parse`
            reads the engine's ``run_id`` text); they are rejected if
            computed again, and a run of the tax year before the last one
            is rejected as out of order.
        gross: Contractual gross earnings paid.
        taxable: IRPEF taxable income.
        inps_base: INPS contribution base.
        inps_employee: Employee INPS contributions withheld.
        irpef_withheld: IRPEF withheld.
        surtax_withheld: Regional and municipal surtax withheld.
        fringe_value: Fringe benefit value granted (Art. 51 c. 3 TUIR).
        fringe_taxed: Part of ``fringe_value`` already taxed.
        pdr: Premio di Risultato taxed at the substitute rate.
        trattamento_recognized: Trattamento integrativo paid.
        trattamento_recovered: Trattamento integrativo already recovered.
        trattamento_due: Annual trattamento integrativo last computed by
            the previous provider, ``None`` when not known.
        trattamento_reason: Lower snake case reason of that amount, e.g.
            ``"full_amount"``, ``None`` when not known.
        somma_esente_recognized: Somma esente (L. 207/2024) paid.
        somma_esente_recovered: Somma esente already recovered.
        somma_esente_due: Annual somma esente last computed, or ``None``.
        somma_esente_reason: Reason of that amount, or ``None``.
        ulteriore_recognized: Ulteriore detrazione (L. 207/2024 art. 1
            c. 6) already applied by the withholding.
        ulteriore_recovered: Ulteriore detrazione already taken back.
        ulteriore_due: Annual ulteriore detrazione last computed, or
            ``None``.
        ulteriore_reason: Reason of that amount, or ``None``.
        irpef_shortfall: IRPEF due on earlier runs and not yet withheld for
            lack of pay.
        surtax_shortfall: Surtax due on earlier runs and not yet withheld.
        work_time_regime_used: Night, holiday and shift supplements already
            taxed at the substitute rate (L. 199/2025 art. 1 cc. 10-11).
        recoveries: Installment recoveries still running, from this tax
            year or an earlier one.
    """

    tax_year: int
    regular_periods_closed: int = 0
    tax_withholding_periods_closed: int = 0
    closed_run_ids: tuple[PayrollRunId, ...] = ()
    gross: Decimal = _ZERO
    taxable: Decimal = _ZERO
    inps_base: Decimal = _ZERO
    inps_employee: Decimal = _ZERO
    irpef_withheld: Decimal = _ZERO
    surtax_withheld: Decimal = _ZERO
    fringe_value: Decimal = _ZERO
    fringe_taxed: Decimal = _ZERO
    pdr: Decimal = _ZERO
    trattamento_recognized: Decimal = _ZERO
    trattamento_recovered: Decimal = _ZERO
    trattamento_due: Decimal | None = None
    trattamento_reason: str | None = None
    somma_esente_recognized: Decimal = _ZERO
    somma_esente_recovered: Decimal = _ZERO
    somma_esente_due: Decimal | None = None
    somma_esente_reason: str | None = None
    ulteriore_recognized: Decimal = _ZERO
    ulteriore_recovered: Decimal = _ZERO
    ulteriore_due: Decimal | None = None
    ulteriore_reason: str | None = None
    irpef_shortfall: Decimal = _ZERO
    surtax_shortfall: Decimal = _ZERO
    work_time_regime_used: Decimal = _ZERO
    recoveries: tuple[RecoveryObligation, ...] = ()

    def __post_init__(self) -> None:
        """Validate every amount and the consistency of the totals.

        Raises:
            InvalidInputError: When the totals do not form a valid state
                (e.g. a negative amount, more recovered than recognized, a
                closed run out of order, a recovery opened after
                ``tax_year``) or an amount is finer than a cent.
        """
        try:
            self.to_state()
        except ValueError as exc:
            raise InvalidInputError(str(exc), feature=_FEATURE) from exc
        for f in fields(self):
            value = getattr(self, f.name)
            if isinstance(value, Decimal):
                _check_cents(f.name, value)

    def to_state(self) -> PeriodState:
        """Return the state to open the next run with.

        Returns:
            A :class:`~ccnl_engine.payroll.domain.period.PeriodState` bound
            to :attr:`tax_year`, carrying :attr:`recoveries`.
        """
        ytd = TaxYearState(
            tax_year=self.tax_year,
            regular_periods_closed=self.regular_periods_closed,
            tax_withholding_periods_closed=self.tax_withholding_periods_closed,
            closed_run_ids=self.closed_run_ids,
            earnings=EarningsYtd(
                gross=self.gross,
                inps_base=self.inps_base,
                taxable=self.taxable,
                inps_employee=self.inps_employee,
            ),
            fringe=FringeYtd(
                value=self.fringe_value, taxed=self.fringe_taxed, pdr=self.pdr
            ),
            tax=TaxYtd(irpef=self.irpef_withheld, surtax=self.surtax_withheld),
            trattamento=TrattamentoAccount(
                recognized=self.trattamento_recognized,
                recovered=self.trattamento_recovered,
                due=self.trattamento_due,
                reason=self.trattamento_reason,
            ),
            somma_esente=SommaEsenteAccount(
                recognized=self.somma_esente_recognized,
                recovered=self.somma_esente_recovered,
                due=self.somma_esente_due,
                reason=self.somma_esente_reason,
            ),
            ulteriore_detrazione=UlterioreDetrazioneAccount(
                recognized=self.ulteriore_recognized,
                recovered=self.ulteriore_recovered,
                due=self.ulteriore_due,
                reason=self.ulteriore_reason,
            ),
            work_time_regime=RegimeCapAccount(used=self.work_time_regime_used),
            shortfall=WithholdingShortfall(
                irpef=self.irpef_shortfall, surtax=self.surtax_shortfall
            ),
        )
        return PeriodState(
            ytd=ytd, obligations=EmploymentObligations(recoveries=self.recoveries)
        )


def _check_cents(name: str, value: Decimal) -> None:
    """Reject an amount finer than a cent.

    Raises:
        InvalidInputError: When ``value`` has more than two decimals.
    """
    if value != value.quantize(_CENT):
        msg = f"OpeningBalances.{name} has more than two decimals; got {value}"
        raise InvalidInputError(msg, feature=_FEATURE)
