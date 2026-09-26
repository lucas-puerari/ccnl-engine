"""Variable-pay events: bonus, fringe, welfare, arrears, bilateral fund."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.period_payroll import PeriodId

__all__ = [
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "FringeEvent",
    "WelfareEvent",
]


@dataclass(frozen=True)
class BonusEvent:
    """One-off bonus: INPS + IRPEF (ordinary or substitute) + TFR excluded.

    Attributes:
        event_date: Date the bonus is attributed to.
        amount: Gross bonus amount in EUR.  Must be >= 0.
        kind: ``"productivity_bonus"`` routes the amount through the PdR
            substitute-tax regime (L. 208/2015 art. 1 cc. 182-190).
            ``"contract_renewal"`` marks a salary increment paid under a CCNL
            renewal, for the renewal substitute-tax regime (L. 199/2025
            art. 1 c. 7).  ``"bonus"`` (the default) applies ordinary IRPEF.
        agreement_signed_on: Signing date of the CCNL renewal a
            ``"contract_renewal"`` increment is paid under.  The renewal
            substitute tax applies only to renewals signed within the window
            of the regime (1 January 2024 to 31 December 2026); ``None``
            means not known: ordinary IRPEF and a provisional result.  Only
            allowed with ``kind="contract_renewal"``.

    The prior-year income and the written waiver the regimes check are
    declared once in
    :class:`~ccnl_engine.payroll.domain.prior_year.PriorYearTaxFacts`.
    """

    event_date: date
    amount: Decimal
    kind: Literal["bonus", "productivity_bonus", "contract_renewal"] = "bonus"
    agreement_signed_on: date | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"BonusEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="bonus")
        if self.agreement_signed_on is not None and self.kind != "contract_renewal":
            msg = (
                "BonusEvent.agreement_signed_on applies only to "
                f"kind='contract_renewal'; got kind={self.kind!r}"
            )
            raise InvalidInputError(msg, feature="bonus")


@dataclass(frozen=True)
class FringeEvent:
    """Fringe benefit (art. 51 co. 3 TUIR).

    The annual exemption threshold is resolved by ``calculate_period`` from
    the year-level ``VariablePayRules.fringe_benefit`` policy — it is not
    carried on the event itself.  Taxability is determined cumulatively
    across all fringe events in the year (YTD + current period).

    Attributes:
        event_date: Date the benefit is attributed to.
        amount: Value of the fringe benefit in EUR.  Must be >= 0.
    """

    event_date: date
    amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"FringeEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="fringe")


@dataclass(frozen=True)
class WelfareEvent:
    """Welfare benefit: exempt from INPS and IRPEF, no TFR accrual.

    Attributes:
        event_date: Date the benefit is attributed to.
        amount: Value of the welfare benefit in EUR.  Must be >= 0.
    """

    event_date: date
    amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"WelfareEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="welfare")


@dataclass(frozen=True)
class ArrearsEvent:
    """Contract renewal arrears subject to tassazione separata (art. 17 TUIR).

    Attributes:
        event_date: Date the arrears are attributed to.
        amount: Gross arrears amount in EUR.  Must be >= 0.
        separate_tax_rate: Caller-supplied average IRPEF rate from the
            two prior tax years, applied as tassazione separata.
            Must be in [0, 1].
        reference_period: The competence period from which the arrears
            originate (e.g. the period of the back-dated contract renewal).
            ``None`` when the reference period is not tracked.
    """

    event_date: date
    amount: Decimal
    separate_tax_rate: Decimal
    reference_period: PeriodId | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"ArrearsEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="arrears")
        if not (0 <= self.separate_tax_rate <= 1):
            msg = (
                "ArrearsEvent.separate_tax_rate must be in [0, 1]; "
                f"got {self.separate_tax_rate}"
            )
            raise InvalidInputError(msg, feature="arrears")


@dataclass(frozen=True)
class BilateralFundEvent:
    """Bilateral or health fund contribution (fondi bilaterali/sanitari).

    Both employee and employer portions are expressed as gross amounts.
    The employee portion reduces net pay; the employer portion increases
    employer cost.

    Attributes:
        event_date: Date the contribution is attributed to.
        employee_amount: Employee-side contribution in EUR.  Must be >= 0.
        employer_amount: EmployerProfile-side contribution in EUR.  Must be >= 0.
    """

    event_date: date
    employee_amount: Decimal
    employer_amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.employee_amount < 0:
            msg = (
                "BilateralFundEvent.employee_amount must be >= 0; "
                f"got {self.employee_amount}"
            )
            raise InvalidInputError(msg, feature="bilateral_fund")
        if self.employer_amount < 0:
            msg = (
                "BilateralFundEvent.employer_amount must be >= 0; "
                f"got {self.employer_amount}"
            )
            raise InvalidInputError(msg, feature="bilateral_fund")
