"""Opening balances imported from a previous payroll provider.

An integration that takes over an employment mid-year, or at the start of
a year with a recovery still running, states the progressive totals of the
previous provider here.  :meth:`OpeningBalances.to_state` validates them
and returns the :class:`~ccnl_engine.payroll.domain.period_state.PeriodState` to
pass as ``opening_state`` to the first run computed by the engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import final

from ccnl_engine.payroll.application.opening_balance_fields import (
    FEATURE,
    check_scalar_fields,
    items,
)
from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.credit_accounts import (
    SommaEsenteAccount,
    TrattamentoAccount,
    UlterioreDetrazioneAccount,
)
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.surtax_obligations import SurtaxObligation
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    TaxYtd,
    WithholdingShortfall,
)
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import require_instance

__all__ = ["OpeningBalances"]

_ZERO = Decimal(0)
_CENT = Decimal("0.01")


@final
@dataclass(frozen=True)
class OpeningBalances:
    """Progressive totals of a tax year computed outside the engine.

    Every amount is in EUR, non-negative and with at most two decimals; an
    amount left ``None`` (a ``*_due``) is not known.
    The totals are validated by the same rules as the state the engine
    produces (:class:`~ccnl_engine.payroll.domain.tax_cash_state.TaxCashState`
    and its accounts); a violation is raised as ``InvalidInputError``.

    Attributes:
        tax_year: Tax year of the totals.
        withholding_payments_closed: Payments of the tax year that already
            took an IRPEF withholding slot (every run kind but adjustment),
            whatever their competence year; no maximum.
        payments: The payments already made this tax year, in payment
            order, when the integration keeps them
            (:meth:`~ccnl_engine.payroll.domain.payment.PaymentId.parse`
            reads ``"2026-12-regular@2027-01-13"``).  Each must belong to
            ``tax_year``; its run is closed in the accrual state, so it is
            rejected if computed again, and a run of the same competence
            year before it is rejected as out of order.  A late payment of
            an earlier competence year takes a slot of the withholding
            schedule of the year.
        gross: Contractual gross earnings paid.
        taxable: IRPEF taxable income.
        inps_base: INPS contribution base.
        inps_employee: Employee INPS contributions withheld.
        pension_deducted: Pension fund contributions already deducted from
            the taxable income (D.Lgs. 252/2005 art. 8 c. 4).
        irpef_withheld: IRPEF withheld.
        surtax_withheld: Regional and municipal surtax withheld.
        municipal_advance_withheld: Part of ``surtax_withheld`` withheld as
            the municipal acconto of ``tax_year`` (D.Lgs. 360/1998 art. 1
            c. 5); the conguaglio deducts it from the municipal surtax.
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
        surtax_obligations: Surtax determined by the conguaglio of an
            earlier tax year and not yet withheld: the regional surtax and
            municipal saldo of ``tax_year - 1`` and the municipal acconto of
            ``tax_year``, by the installments still to post.  For a worker
            employed in the previous year, import them: the engine
            withholds no surtax the previous provider determined unless it
            is stated here.
        deferred_shortfall: IRPEF the conguaglio of ``tax_year - 1``
            deferred on the worker's written request (art. 23 c. 3 DPR
            600/1973) and not yet withheld, ``None`` without one.
    """

    tax_year: int
    withholding_payments_closed: int = 0
    payments: tuple[PaymentId, ...] = ()
    gross: Decimal = _ZERO
    taxable: Decimal = _ZERO
    inps_base: Decimal = _ZERO
    inps_employee: Decimal = _ZERO
    pension_deducted: Decimal = _ZERO
    irpef_withheld: Decimal = _ZERO
    surtax_withheld: Decimal = _ZERO
    municipal_advance_withheld: Decimal = _ZERO
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
    surtax_obligations: tuple[SurtaxObligation, ...] = ()
    deferred_shortfall: DeferredShortfall | None = None

    def __post_init__(self) -> None:
        """Validate every amount and the consistency of the totals.

        Raises:
            InvalidInputError: When the totals do not form a valid state
                (e.g. a negative amount, more recovered than recognized, a
                closed run out of order, a recovery opened after
                ``tax_year``, surtax determined by the conguaglio of
                ``tax_year`` or later, a deferral of a conguaglio other than
                that of ``tax_year - 1``) or an amount is finer than a cent.
        """
        check_scalar_fields(self)
        object.__setattr__(
            self, "payments", items(self.payments, "payments", PaymentId)
        )
        object.__setattr__(
            self, "recoveries", items(self.recoveries, "recoveries", RecoveryObligation)
        )
        object.__setattr__(
            self,
            "surtax_obligations",
            items(self.surtax_obligations, "surtax_obligations", SurtaxObligation),
        )
        require_instance(
            self.deferred_shortfall,
            DeferredShortfall,
            "OpeningBalances.deferred_shortfall",
            feature=FEATURE,
            optional=True,
        )
        deferred = self.deferred_shortfall
        if deferred is not None and deferred.tax_year != self.tax_year - 1:
            msg = (
                "OpeningBalances.deferred_shortfall must be deferred by the "
                f"conguaglio of {self.tax_year - 1}; got {deferred.tax_year}"
            )
            raise InvalidInputError(
                msg, field="OpeningBalances.deferred_shortfall", feature=FEATURE
            )
        late = [o for o in self.surtax_obligations if o.tax_year >= self.tax_year]
        if late:
            msg = (
                f"OpeningBalances.surtax_obligations must be determined by "
                f"the conguaglio of a year before {self.tax_year}; got "
                f"{[(o.component.value, o.tax_year) for o in late]}"
            )
            raise InvalidInputError(
                msg, field="OpeningBalances.surtax_obligations", feature=FEATURE
            )
        try:
            self.to_state()
        except (ValueError, InvalidInputError) as exc:
            raise InvalidInputError(
                str(exc), field=getattr(exc, "field", None), feature=FEATURE
            ) from exc

    def to_state(self) -> PeriodState:
        """Return the state to open the next run with.

        Returns:
            A :class:`~ccnl_engine.payroll.domain.period_state.PeriodState` bound
            to :attr:`tax_year`, carrying :attr:`recoveries`,
            :attr:`surtax_obligations` and :attr:`deferred_shortfall`.
        """
        cash = TaxCashState(
            tax_year=self.tax_year,
            payments=self.payments,
            withholding_payments_closed=self.withholding_payments_closed,
            earnings=EarningsYtd(
                gross=self.gross,
                inps_base=self.inps_base,
                taxable=self.taxable,
                inps_employee=self.inps_employee,
                pension_deducted=self.pension_deducted,
            ),
            fringe=FringeYtd(
                value=self.fringe_value, taxed=self.fringe_taxed, pdr=self.pdr
            ),
            tax=TaxYtd(
                irpef=self.irpef_withheld,
                surtax=self.surtax_withheld,
                municipal_advance=self.municipal_advance_withheld,
            ),
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
            obligations=EmploymentObligations(
                recoveries=self.recoveries,
                surtax=self.surtax_obligations,
                deferred_shortfall=(
                    ()
                    if self.deferred_shortfall is None
                    else (self.deferred_shortfall,)
                ),
            ),
        )
        accrual = EmploymentAccrualState(
            competence_runs=tuple(p.run_id for p in self.payments)
        )
        return PeriodState(accrual=accrual, cash=cash)
