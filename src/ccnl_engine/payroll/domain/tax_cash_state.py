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
from typing import final

from ccnl_engine.payroll.domain.credit_accounts import (
    SommaEsenteAccount,
    TrattamentoAccount,
    UlterioreDetrazioneAccount,
)
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
        payments: Payments closed this tax year, in closing order.  Each
            belongs to :attr:`tax_year` and pays a different run; their
            number has no maximum.  Integrations that do not keep payment
            ids may leave it empty and state only
            :attr:`withholding_payments_closed`.
        withholding_payments_closed: Payments of this tax year that took an
            IRPEF withholding slot (every run kind but adjustment), at
            least as many as such payments in :attr:`payments`.  The
            projection and the conguaglio divide the tax still due over
            the slots of the withholding schedule after these.
        withholding_slots: Slots of the withholding schedule the last run
            was computed on: the payments planned for the tax year, the
            last of which settles the conguaglio.  ``None`` before the
            first run.
        earnings: Running totals for earned income and INPS contribution
            bases (gross, taxable, INPS base, employee INPS).
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

    Raises:
        InvalidInputError: When a field is not of its type, a payment
            belongs to another tax year or is repeated, the withholding
            counters are out of range, or an obligation is opened after
            :attr:`tax_year`.
    """

    tax_year: int | None = None
    payments: tuple[PaymentId, ...] = ()
    withholding_payments_closed: int = 0
    withholding_slots: int | None = None
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

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.tax_year,
            f"{_OWNER}.tax_year",
            feature=_FEATURE,
            minimum=_MIN_TAX_YEAR,
            maximum=_MAX_TAX_YEAR,
            optional=True,
        )
        require_int(
            self.withholding_payments_closed,
            f"{_OWNER}.withholding_payments_closed",
            feature=_FEATURE,
            minimum=0,
        )
        require_int(
            self.withholding_slots,
            f"{_OWNER}.withholding_slots",
            feature=_FEATURE,
            minimum=1,
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
        )

    def _check_payments(self) -> None:
        """Validate :attr:`payments` against the tax year and the counter.

        Raises:
            InvalidInputError: When payments are not bound to a tax year,
                belong to another one, pay a run twice, or outnumber
                :attr:`withholding_payments_closed`.
        """
        path = f"{_OWNER}.payments"
        if not self.payments:
            return
        if self.tax_year is None:
            msg = f"{path} requires a tax_year"
            raise InvalidInputError(msg, field=path, feature=_FEATURE)
        seen: list[PaymentId] = []
        for payment in self.payments:
            _check_payment(tuple(seen), payment, self.tax_year)
            seen.append(payment)
        slots = sum(1 for p in self.payments if p.run_id.kind.consumes_withholding_slot)
        if slots > self.withholding_payments_closed:
            msg = (
                f"{path} holds {slots} slot-consuming payments but "
                f"withholding_payments_closed is {self.withholding_payments_closed}"
            )
            raise InvalidInputError(msg, field=path, feature=_FEATURE)

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

        A payment of a run already paid this tax year, or of another tax
        year, raises ``InvalidInputError``.
        """
        _check_payment(self.payments, payment, self.tax_year)

    @property
    def prior_competence_payments(self) -> tuple[PaymentId, ...]:
        """Payments of this tax year that settle runs of an earlier year."""
        return tuple(p for p in self.payments if p.is_prior_competence)

    @property
    def is_complete(self) -> bool:
        """Whether every withholding slot of the year has been closed.

        Returns:
            ``True`` when a run has recorded ``withholding_slots`` and
            ``withholding_payments_closed`` has reached it.
        """
        return (
            self.withholding_slots is not None
            and self.withholding_payments_closed >= self.withholding_slots
        )


def _check_payment(
    closed: tuple[PaymentId, ...], payment: PaymentId, tax_year: int | None
) -> None:
    """Check that ``payment`` can close after the payments ``closed``.

    Raises:
        InvalidInputError: When the run of ``payment`` is paid in
            ``closed`` or ``payment`` is not of ``tax_year``.
    """
    path = f"{_OWNER}.payments"
    if any(p.run_id == payment.run_id for p in closed):
        msg = (
            f"payment '{payment}': run '{payment.run_id}' is already paid in "
            "this tax year; a retry of a payment must open with the state "
            "before it"
        )
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    if tax_year is not None and payment.tax_year != tax_year:
        msg = (
            f"payment '{payment}' belongs to tax year {payment.tax_year}, "
            f"not {tax_year}"
        )
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
