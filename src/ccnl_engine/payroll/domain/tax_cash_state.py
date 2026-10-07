"""Cash state of one tax year: payments, YTD accounts and carried obligations.

Everything here except :attr:`TaxCashState.obligations` belongs to a single
tax year and restarts from zero when the next tax year opens
(:func:`~ccnl_engine.payroll.application.close_tax_year.close_tax_year`).
A tax year counts the payments made in it, whatever their competence:
December 2026 paid on 13 January 2027 is a payment of 2027 (TUIR art. 51
c. 1), so a tax year can hold more than fourteen payments and no maximum
is set on them.  The competence months closed are counted by
:class:`~ccnl_engine.payroll.domain.accrual_state.EmploymentAccrualState`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, final

from ccnl_engine.payroll.domain.credit_accounts import (
    SommaEsenteAccount,
    TrattamentoAccount,
    UlterioreDetrazioneAccount,
)
from ccnl_engine.payroll.domain.employment_spells import EmploymentSpell, spells_of
from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    TaxYtd,
    WithholdingShortfall,
)
from ccnl_engine.shared.domain.collection_validation import items_of_type, tuple_of
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import (
    FieldSpec,
    require_instances,
    require_int,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.run import PayrollRunId

__all__ = ["TaxCashState"]

_FEATURE = "tax_cash_state"
_OWNER = "TaxCashState"
_MIN_TAX_YEAR = 2020
_MAX_TAX_YEAR = 9999


@final
@dataclass(frozen=True)
class TaxCashState:
    """Payments, YTD accounts and carried obligations of one tax year.

    Attributes:
        tax_year: Tax year of the payments and accounts.  ``None`` on a
            manually built state not yet bound to a year; every state
            produced by a run carries it.
        payments: Payments closed this tax year, in payment order: each
            belongs to :attr:`tax_year`, pays a different run and is dated
            on or after the payment before it.  Their number has no
            maximum.  The withholding schedule reads which of its slots are
            paid from them, by run.
        conguaglio: The payment that settled the conguaglio of the tax year:
            the last payment that takes a withholding slot, when it left no
            slot of its schedule unpaid.  ``None`` until then, and again
            after a later payment that takes a slot without settling.
        earnings: Running totals for earned income (gross, taxable,
            employee INPS, pension deductions).  The INPS base, which
            follows competence, is in the accrual state.
        fringe: Running totals for fringe benefits and PdR (value, taxed
            base, PdR eligible amount).
        tax: Running totals for tax withheld this year (IRPEF, surtax).
        trattamento: YTD credit account for trattamento integrativo of this
            tax year.  Installments of a recovery carried from an earlier
            year do not enter it.
        somma_esente: YTD credit account for the somma esente bonus
            (L. 207/2024).
        ulteriore_detrazione: YTD account of the ulteriore detrazione
            (L. 207/2024 art. 1 c. 6) recognized by the withholding.
        work_time_regime: YTD usage of the annual cap of the night, holiday
            and shift supplement substitute tax (L. 199/2025 art. 1
            cc. 10-11).
        shortfall: IRPEF and surtax due on earlier runs and not yet
            withheld because the pay left did not cover them.
        obligations: Obligations carried into this tax year and still
            running, such as an installment recovery, the surtax a
            conguaglio determined or the IRPEF of a conguaglio deferred on
            written request.  None is opened after :attr:`tax_year`.
        employment_spells: Days in :attr:`tax_year` of each employment the
            payments paid, in order of first day: the art. 13 TUIR
            deduction counts their union
            (:mod:`~ccnl_engine.payroll.domain.employment_spells`).

    Raises:
        InvalidInputError: When a field is not of its type, a payment
            belongs to another tax year, is repeated or is dated before the
            payment closed before it, :attr:`conguaglio` is not the last
            payment that takes a slot, or an obligation is opened after
            :attr:`tax_year`, or a spell is of another year.
    """

    tax_year: int | None = None
    payments: tuple[PaymentId, ...] = ()
    conguaglio: PaymentId | None = None
    earnings: EarningsYtd = field(default_factory=EarningsYtd)
    fringe: FringeYtd = field(default_factory=FringeYtd)
    tax: TaxYtd = field(default_factory=TaxYtd)
    trattamento: TrattamentoAccount = field(default_factory=TrattamentoAccount)
    somma_esente: SommaEsenteAccount = field(default_factory=SommaEsenteAccount)
    ulteriore_detrazione: UlterioreDetrazioneAccount = field(
        default_factory=UlterioreDetrazioneAccount
    )
    work_time_regime: RegimeCapAccount = field(default_factory=RegimeCapAccount)
    shortfall: WithholdingShortfall = field(default_factory=WithholdingShortfall)
    obligations: EmploymentObligations = field(default_factory=EmploymentObligations)
    employment_spells: tuple[EmploymentSpell, ...] = ()

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.tax_year,
            f"{_OWNER}.tax_year",
            feature=_FEATURE,
            minimum=_MIN_TAX_YEAR,
            maximum=_MAX_TAX_YEAR,
            optional=True,
        )
        require_instances(_OWNER, self._account_specs(), feature=_FEATURE)
        payments = tuple_of(
            self.payments,
            f"{_OWNER}.payments",
            items_of_type(PaymentId, feature=_FEATURE),
            feature=_FEATURE,
        )
        object.__setattr__(self, "payments", payments)
        spells = spells_of(
            self.employment_spells, f"{_OWNER}.employment_spells", self.tax_year
        )
        object.__setattr__(self, "employment_spells", spells)
        self._check_payments()
        self._check_obligations()

    def _account_specs(self) -> tuple[FieldSpec, ...]:
        """Return the account fields with their types.

        Returns:
            One spec per account field.
        """
        return (
            ("earnings", self.earnings, EarningsYtd, False),
            ("fringe", self.fringe, FringeYtd, False),
            ("tax", self.tax, TaxYtd, False),
            ("trattamento", self.trattamento, TrattamentoAccount, False),
            ("somma_esente", self.somma_esente, SommaEsenteAccount, False),
            (
                "ulteriore_detrazione",
                self.ulteriore_detrazione,
                UlterioreDetrazioneAccount,
                False,
            ),
            ("work_time_regime", self.work_time_regime, RegimeCapAccount, False),
            ("shortfall", self.shortfall, WithholdingShortfall, False),
            ("obligations", self.obligations, EmploymentObligations, False),
            ("conguaglio", self.conguaglio, PaymentId, True),
        )

    def _check_payments(self) -> None:
        """Validate :attr:`payments` against the tax year and the counter.

        Raises:
            InvalidInputError: When payments are not bound to a tax year,
                belong to another one, pay a run twice or go back in time,
                or :attr:`conguaglio` is not the last payment that takes a
                withholding slot.
        """
        path = f"{_OWNER}.payments"
        if self.payments and self.tax_year is None:
            msg = f"{path} requires a tax_year"
            raise InvalidInputError(msg, field=path, feature=_FEATURE)
        for index, payment in enumerate(self.payments):
            _check_payment(self.payments[:index], payment, self.tax_year)
        slots = [p for p in self.payments if p.run_id.kind.consumes_withholding_slot]
        if self.conguaglio is not None and (not slots or slots[-1] != self.conguaglio):
            msg = (
                f"conguaglio '{self.conguaglio}' must be the last payment of "
                "the tax year that takes a withholding slot"
            )
            raise InvalidInputError(msg, field=f"{_OWNER}.conguaglio", feature=_FEATURE)

    def _check_obligations(self) -> None:
        """Reject an obligation opened after :attr:`tax_year`.

        Raises:
            InvalidInputError: When a recovery or surtax obligation
                originates in a year later than :attr:`tax_year`.
        """
        latest = self.obligations.latest_tax_year
        if self.tax_year is not None and latest is not None and latest > self.tax_year:
            msg = (
                f"obligations include one opened in {latest}, after the "
                f"tax year of the state ({self.tax_year})"
            )
            raise InvalidInputError(
                msg, field=f"{_OWNER}.obligations", feature=_FEATURE
            )

    def check_next_payment(self, payment: PaymentId) -> None:
        """Check that ``payment`` can close next in this tax year.

        A payment of a run already paid this tax year, of another tax year,
        or dated before the last payment closed raises
        ``InvalidInputError``.
        """
        _check_payment(self.payments, payment, self.tax_year)

    @property
    def withholding_payments_closed(self) -> int:
        """Payments of the tax year that took a withholding slot.

        Every run kind takes one but an adjustment run.
        """
        return sum(1 for p in self.payments if p.run_id.kind.consumes_withholding_slot)

    @property
    def paid_runs(self) -> frozenset[PayrollRunId]:
        """Runs paid this tax year: the slots of the schedule already taken."""
        return frozenset(p.run_id for p in self.payments)

    @property
    def prior_competence_payments(self) -> tuple[PaymentId, ...]:
        """Payments of this tax year that settle runs of an earlier year."""
        return tuple(p for p in self.payments if p.is_prior_competence)

    @property
    def is_complete(self) -> bool:
        """Whether the last payment that took a slot settled the conguaglio."""
        return self.conguaglio is not None


def _check_payment(
    closed: tuple[PaymentId, ...], payment: PaymentId, tax_year: int | None
) -> None:
    """Check that ``payment`` can close after the payments ``closed``.

    Raises:
        InvalidInputError: When the run of ``payment`` is paid in
            ``closed``, ``payment`` is not of ``tax_year``, or it is dated
            before the last payment of ``closed``.
    """
    path = f"{_OWNER}.payments"
    if any(p.run_id.payment_key == payment.run_id.payment_key for p in closed):
        msg = (
            f"payment '{payment}': run '{payment.run_id}' is already paid in "
            "this tax year; a retry of a payment must open with the state "
            "before it"
        )
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    if closed and payment.payment_date < closed[-1].payment_date:
        msg = (
            f"payment '{payment}' is dated before payment '{closed[-1]}', "
            "already closed: the payments of a tax year close in payment "
            "order, because each withholding reads the totals of the "
            "payments made before it"
        )
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    if tax_year is not None and payment.tax_year != tax_year:
        msg = (
            f"payment '{payment}' belongs to tax year {payment.tax_year}, "
            f"not {tax_year}"
        )
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
