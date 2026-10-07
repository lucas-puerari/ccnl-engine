"""Opening balances imported from a previous payroll provider.

An integration taking over an employment states the totals of the previous
provider here and imports them with
:meth:`~ccnl_engine.api.facade.PayrollEngine.import_opening_balances`, the
one way to build a state the engine did not compute.  Each payment behind
the totals is identified, so the engine never computes it again.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import final

from ccnl_engine.payroll.application.opening_balance_fields import (
    FEATURE,
    check_bases,
    check_carried,
    check_scalar_fields,
    items,
)
from ccnl_engine.payroll.application.opening_state import opening_state
from ccnl_engine.payroll.domain.employment_spells import EmploymentSpell
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.obligations import (
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.sickness import SicknessEpisode
from ccnl_engine.payroll.domain.surtax_obligations import SurtaxObligation
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
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
    amount left ``None`` (a ``*_due``) is not known.  The totals are
    validated by the same rules as the state the engine produces
    (:class:`~ccnl_engine.payroll.domain.period_state.PeriodState`); a
    violation is raised as ``InvalidInputError``.  A tax-year total without
    the payments that produced it is rejected: it could not be told apart
    from the payments the engine would compute again.  The INPS bases and
    the obligations carried from an earlier run have no default: what the
    previous provider determined is a fact the import states, ``()`` when
    there is none.

    Attributes:
        tax_year: Tax year of the totals.
        payments: The payments already made this tax year, in payment order
            (:meth:`~ccnl_engine.payroll.domain.payment.PaymentId.parse`
            reads ``"2026-12-regular@2027-01-13"``), whatever their
            competence year.  Each must belong to ``tax_year``; its run is
            closed, so it is rejected if computed again, and each takes a
            slot of the withholding schedule of the year but an adjustment.
        competence_runs: Runs closed in earlier tax years that a run still
            to compute must follow: with December 2026 paid on 13 January
            2027, the other 2026 runs paid in 2026.  Payments of
            ``tax_year`` go in ``payments``, not here.
        inps_bases: Required.  INPS base toward the IVS massimale per
            competence year: this employment's (``own``) and the worker's
            other employments of the same year (``other_employers``, from
            their CU or the worker's declaration; INPS circ. 237/2016 par.
            3.1; ``None`` when not known, which blocks the runs whose
            contributions could depend on it), with the additional 1% IVS
            each withheld on it (``additional_ivs``,
            ``other_employers_additional_ivs``).  Every competence year of
            ``payments`` and ``competence_runs`` needs its base; import the
            year before too when its December is paid in ``tax_year``.
        sickness_episodes: Sickness episodes of the employment up to the
            last processed day, in start order: they set the waiting
            period, INPS days and CCNL tier of later episodes.
        sickness_known_from: First day from which ``sickness_episodes``
            list every sick day of the employment: the first day of the
            employment when they list all of them.  ``None`` states the
            episodes of ``tax_year`` only (from 1 January).  A CCNL that
            counts the sickness of earlier years (Federmeccanica: the
            comporto over three years) has a ``missing_fact`` blocker when
            the days before it could change a sick day it pays.
        gross: Contractual gross earnings paid.
        taxable: IRPEF taxable income.
        inps_employee: Employee INPS contributions withheld.
        pension_deducted: Pension fund contributions already deducted from
            the taxable income (D.Lgs. 252/2005 art. 8 c. 4).
        irpef_withheld: IRPEF withheld.
        surtax_withheld: Regional and municipal surtax withheld.
        municipal_advance_withheld: Part of ``surtax_withheld`` withheld as
            the municipal acconto of ``tax_year`` (D.Lgs. 360/1998 art. 1
            c. 5); the conguaglio deducts it from the municipal surtax.
        regional_settled: Regional surtax of ``tax_year`` a conguaglio at
            the end of an earlier employment of the year already withheld.
        municipal_settled: Municipal saldo of ``tax_year`` withheld the
            same way.
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
        credit_recovery_shortfall: Credit recoveries (trattamento
            integrativo, somma esente, installments) due on earlier runs
            and not yet withheld for lack of pay.
        work_time_regime_used: Night, holiday and shift supplements already
            taxed at the substitute rate (L. 199/2025 art. 1 cc. 10-11).
        recoveries: Required.  Installment recoveries still running, from
            this tax year or an earlier one; ``()`` states that there is
            none.
        surtax_obligations: Surtax determined by the conguaglio of an
            earlier tax year and not yet withheld: the regional surtax and
            municipal saldo of ``tax_year - 1`` and the municipal acconto of
            ``tax_year``, by the installments still to post.  Required:
            the engine withholds no surtax the previous provider determined
            unless it is stated here; ``()`` states that there is none.
        deferred_shortfall: IRPEF the conguaglio of ``tax_year - 1``
            deferred on the worker's written request (art. 23 c. 3 DPR
            600/1973) and not yet withheld, ``None`` without one.
        employment_spells: Days in ``tax_year`` of the employments whose
            income the totals hold, when they hold an earlier employment
            with this employer (a rehire): the art. 13 TUIR deduction counts
            their union.  ``()`` states none: the next run adds the days of
            its own employment.
    """

    tax_year: int
    payments: tuple[PaymentId, ...] = ()
    competence_runs: tuple[PayrollRunId, ...] = ()
    inps_bases: tuple[InpsBaseYtd, ...] = field(kw_only=True)
    sickness_episodes: tuple[SicknessEpisode, ...] = ()
    sickness_known_from: date | None = None
    gross: Decimal = _ZERO
    taxable: Decimal = _ZERO
    inps_employee: Decimal = _ZERO
    pension_deducted: Decimal = _ZERO
    irpef_withheld: Decimal = _ZERO
    surtax_withheld: Decimal = _ZERO
    municipal_advance_withheld: Decimal = _ZERO
    regional_settled: Decimal = _ZERO
    municipal_settled: Decimal = _ZERO
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
    credit_recovery_shortfall: Decimal = _ZERO
    work_time_regime_used: Decimal = _ZERO
    recoveries: tuple[RecoveryObligation, ...] = field(kw_only=True)
    surtax_obligations: tuple[SurtaxObligation, ...] = field(kw_only=True)
    deferred_shortfall: DeferredShortfall | None = None
    employment_spells: tuple[EmploymentSpell, ...] = ()

    def __post_init__(self) -> None:
        """Validate every amount and the consistency of the totals.

        Raises:
            InvalidInputError: When the totals do not form a valid state
                (e.g. a negative amount, more recovered than recognized, a
                closed run out of order or closed twice, totals without
                payments, a recovery opened after
                ``tax_year``, surtax determined by the conguaglio of
                ``tax_year`` or later, a deferral of a conguaglio other than
                that of ``tax_year - 1``, a closed run of a competence year
                without its INPS base) or an amount is finer than a cent.
        """
        check_scalar_fields(self)
        for name, item in (
            ("payments", PaymentId),
            ("competence_runs", PayrollRunId),
            ("inps_bases", InpsBaseYtd),
            ("sickness_episodes", SicknessEpisode),
            ("employment_spells", EmploymentSpell),
        ):
            object.__setattr__(self, name, items(getattr(self, name), name, item))
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
        check_carried(self.tax_year, self.deferred_shortfall, self.surtax_obligations)
        try:
            cash = opening_state(self).cash
        except (ValueError, InvalidInputError) as exc:
            raise InvalidInputError(
                str(exc), field=getattr(exc, "field", None), feature=FEATURE
            ) from exc
        if not self.payments and cash != TaxCashState(
            tax_year=self.tax_year, obligations=cash.obligations
        ):
            msg = (
                "OpeningBalances totals need the payments that produced them: "
                "list them in payments"
            )
            raise InvalidInputError(
                msg, field="OpeningBalances.payments", feature=FEATURE
            )
        check_bases(self.payments, self.competence_runs, self.inps_bases)
