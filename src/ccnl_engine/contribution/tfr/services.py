"""The TFR of a run: the art. 2120 c.c. quota and its destination."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.employment.fact.inputs import PublicEndOfService
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _ZERO

if TYPE_CHECKING:
    from ccnl_engine.amount.types import _AmountsInput
    from ccnl_engine.contribution.results import ContributionBreakdown

__all__ = ["TFR_TREASURY_FUND_CODE", "TfrAccrual", "ivs_employer_base", "tfr_accrual"]

#: Regimes whose TFR the employer does not accrue.
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
#: Code of the issue of a TFR whose Fondo Tesoreria destination is unknown.
TFR_TREASURY_FUND_CODE = "tfr_treasury_fund_unknown"


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
        to_pension_fund: The TFR is paid to the complementary pension fund
            the worker is enrolled in.
        fund_share: The share of it paid to the fund; the rest stays in the
            company or goes to the Fondo Tesoreria.
        treasury_fund: The TFR not paid to a pension fund is paid to the
            Fondo Tesoreria INPS (L. 296/2006 art. 1 c. 756); ``None`` when
            the request does not say.
        public: End-of-service regime of a public employee: under the TFS
            no TFR accrues, under the TFR at INPS it accrues notionally at
            INPS (DPCM 20 dicembre 1999 art. 1 c. 6); neither is posted.
    """

    quota: Decimal
    ivs_base: Decimal = _ZERO
    ivs_rate: Decimal = _ZERO
    deduction: Decimal = _ZERO
    to_pension_fund: bool = False
    fund_share: Decimal = Decimal(1)
    treasury_fund: bool | None = False
    public: PublicEndOfService | None = None

    @property
    def notional(self) -> bool:
        """Whether INPS, not the employer, accrues the TFR of the run."""
        return self.public in _AT_INPS

    @property
    def fund_amount(self) -> Decimal:
        """TFR of the run paid to the pension fund."""
        return money(self.amount * self.fund_share) if self.to_pension_fund else _ZERO

    @property
    def paid_share(self) -> Decimal:
        """Share of the TFR of the run paid to the pension fund."""
        return self.fund_share if self.to_pension_fund else _ZERO

    @property
    def account_amount(self) -> Decimal:
        """TFR posted to :attr:`account`: the fund share, or all of it."""
        return self.fund_amount if self.to_pension_fund else self.amount

    @property
    def kept_amount(self) -> Decimal:
        """TFR of the run not paid to the pension fund."""
        return self.amount - self.fund_amount

    @property
    def kept_account(self) -> AccountKind:
        """Account of the TFR not paid to the pension fund."""
        return (
            AccountKind.TFR_TREASURY_FUND
            if self.treasury_fund
            else AccountKind.TFR_ACCRUAL
        )

    @property
    def conferred_share(self) -> Decimal:
        """Share of the TFR of the run that leaves the company for a fund.

        The pension fund share, plus the rest when it goes to the Fondo
        Tesoreria; zero when INPS accrues the TFR.
        """
        if self.notional:
            return _ZERO
        fund = self.fund_share if self.to_pension_fund else _ZERO
        return fund + (Decimal(1) - fund if self.treasury_fund is True else _ZERO)

    @property
    def conferred(self) -> bool:
        """Whether the TFR of the run leaves the company for a fund.

        True when it goes to the pension fund or to the Fondo Tesoreria;
        False when it stays in the company, when INPS accrues it and while
        the Fondo Tesoreria destination is unknown.
        """
        return self.conferred_share > _ZERO

    @property
    def amount(self) -> Decimal:
        """TFR accrued on the run, in the company or paid to a fund."""
        return _ZERO if self.notional else self.quota - self.deduction

    @property
    def destination(self) -> str:
        """Where the TFR of the run goes: an account, or the INPS regime."""
        if self.public is PublicEndOfService.TFS:
            return "tfs"
        return "inps_notional" if self.notional else self.account.value

    @property
    def account(self) -> AccountKind:
        """Account the TFR of the run is posted to.

        The pension fund when the worker pays the TFR to it, else the
        Fondo Tesoreria when the employer pays it there, else the company
        accrual (also while the Fondo Tesoreria destination is unknown).
        """
        if self.to_pension_fund:
            return AccountKind.PENSION_FUND_TFR
        return self.kept_account

    def issues(self) -> tuple[CalculationIssue, ...]:
        """Return the issue of a TFR whose destination is unknown.

        Returns:
            One ``missing_fact`` issue for ``tfr_treasury_fund`` when a
            non-zero TFR stays out of a pension fund and the request does
            not say whether it goes to the Fondo Tesoreria; nothing else.
        """
        if self.treasury_fund is not None or not self.kept_amount:
            return ()
        return (
            CalculationIssue(
                code=TFR_TREASURY_FUND_CODE,
                capability="tfr",
                message=(
                    "tfr: whether the TFR goes to the Fondo Tesoreria INPS "
                    "(L. 296/2006 art. 1 c. 756) is not known; it is posted to "
                    "tfr_accrual: set Employment.tfr_treasury_fund"
                ),
                status=CalculationStatus.PROVISIONAL,
                fact="tfr_treasury_fund",
            ),
        )


def _tfr_paid_to_fund(inp: _AmountsInput) -> bool:
    """Return whether the TFR of the run is paid to the pension fund.

    A public employee's TFR conferred to the fund is not paid: INPS
    Gestione Dipendenti Pubblici accrues it notionally and pays it at the
    termination (Perseo Sirio and Espero, Scheda 'I destinatari e i
    contributi'), so it stays where the run accrues it.

    Returns:
        True when the worker confers the TFR and it is paid to the fund.
    """
    pension = inp.pension
    return pension is not None and pension.tfr_to_fund and not pension.tfr_notional


def ivs_employer_base(breakdown: ContributionBreakdown) -> Decimal:
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
    IVS rule accrue the whole quota; so do apprentices, for whom the
    contribution is not due (INPS circ. 70/2007, note 5).  The Fondo
    Tesoreria takes the quota net of the deduction (L. 296/2006 art. 1
    c. 756).  The base counts the benefits provided in kind (CCNL lavoro
    domestico art. 41 c. 1: the valore convenzionale of board and lodging).

    Returns:
        The quota over the accrual divisor, the deduction taken from it and
        its destination.
    """
    tfr = inp.rules.tfr
    base = inp.tfr_pay
    quota = money(base / tfr.accrual_divisor) + inp.extra_tfr_quota
    public = inp.public.end_of_service
    accrual = TfrAccrual(
        quota=_ZERO if public is PublicEndOfService.TFS else quota,
        to_pension_fund=_tfr_paid_to_fund(inp),
        fund_share=Decimal(1) if inp.pension is None else inp.pension.tfr_share,
        treasury_fund=inp.tfr_treasury_fund,
        public=public,
    )
    extra = tfr.additional_ivs
    if extra is None or isinstance(inp.contract_type, Apprentice):
        return accrual
    ivs_base = ivs_employer_base(breakdown)
    deduction = min(quota, money(ivs_base * extra.rate))
    return replace(accrual, ivs_base=ivs_base, ivs_rate=extra.rate, deduction=deduction)
