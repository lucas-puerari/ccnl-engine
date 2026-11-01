"""Variable-pay events: bonus, fringe, welfare, arrears, bilateral fund."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.run.types import PeriodId
from ccnl_engine.validators import (
    require_bool,
    require_choice,
    require_date,
    require_decimal,
    require_instance,
    require_int,
)

if TYPE_CHECKING:
    from datetime import date

_ZERO = Decimal(0)
_ONE = Decimal(1)
_BONUS_KINDS = ("bonus", "productivity_bonus", "contract_renewal")
_MEALS_LODGING = ("none", "one", "both")
_TFR_BASES = ("none", "whole", "above_exempt")


def _check_amount(event_date: object, amount: object, event: str, feature: str) -> None:
    """Reject an event without a date or with a negative amount."""
    require_date(event_date, f"{event}.event_date", feature=feature)
    require_decimal(amount, f"{event}.amount", feature=feature, minimum=_ZERO)


__all__ = [
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "FringeEvent",
    "TravelAllowanceEvent",
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
    :class:`~ccnl_engine.irpef.declaration.inputs.PriorYearTaxFacts`.
    """

    event_date: date
    amount: Decimal
    kind: Literal["bonus", "productivity_bonus", "contract_renewal"] = "bonus"
    agreement_signed_on: date | None = None

    def __post_init__(self) -> None:  # noqa: D105
        _check_amount(self.event_date, self.amount, "BonusEvent", "bonus")
        require_choice(self.kind, _BONUS_KINDS, "BonusEvent.kind", feature="bonus")
        require_date(
            self.agreement_signed_on,
            "BonusEvent.agreement_signed_on",
            feature="bonus",
            optional=True,
        )
        if self.agreement_signed_on is not None and self.kind != "contract_renewal":
            msg = (
                "BonusEvent.agreement_signed_on applies only to "
                f"kind='contract_renewal'; got kind={self.kind!r}"
            )
            raise InvalidInputError(
                msg, field="BonusEvent.agreement_signed_on", feature="bonus"
            )


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
        _check_amount(self.event_date, self.amount, "FringeEvent", "fringe")


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
        _check_amount(self.event_date, self.amount, "WelfareEvent", "welfare")


@dataclass(frozen=True)
class ArrearsEvent:
    """Contract renewal arrears, taxed by the year they refer to.

    Arrears of a tax year earlier than the run are taxed separately (art. 17
    c. 1 lett. b TUIR; art. 19 c. 1 lett. b D.Lgs. 117/2026 from 2027) at
    :attr:`separate_tax_rate`; arrears of the tax year
    of the run are ordinary income of the run and the rate is not used.

    Attributes:
        event_date: Date the arrears are attributed to.
        amount: Gross arrears amount in EUR.  Must be >= 0.
        separate_tax_rate: Rate of the separate taxation: the rate on half
            the income of the two years before the year of receipt (art. 21
            c. 1 TUIR; art. 23 c. 1 D.Lgs. 117/2026 from 2027), in [0, 1].
            ``None``: the engine computes it from
            ``PriorYearTaxFacts.net_income_biennio``.
        reference_period: The competence period the arrears refer to.  An
            earlier tax year selects the separate taxation, the tax year of
            the run the ordinary one, a later year is rejected.  ``None``
            leaves the taxation undetermined: the run taxes the arrears
            separately as a simulation, with a ``missing_fact`` blocker.
    """

    event_date: date
    amount: Decimal
    separate_tax_rate: Decimal | None = None
    reference_period: PeriodId | None = None

    def __post_init__(self) -> None:  # noqa: D105
        _check_amount(self.event_date, self.amount, "ArrearsEvent", "arrears")
        require_decimal(
            self.separate_tax_rate,
            "ArrearsEvent.separate_tax_rate",
            feature="arrears",
            minimum=_ZERO,
            maximum=_ONE,
            optional=True,
        )
        require_instance(
            self.reference_period,
            PeriodId,
            "ArrearsEvent.reference_period",
            feature="arrears",
            optional=True,
        )


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
        feature = "bilateral_fund"
        require_date(self.event_date, "BilateralFundEvent.event_date", feature=feature)
        for name in ("employee_amount", "employer_amount"):
            require_decimal(
                getattr(self, name),
                f"BilateralFundEvent.{name}",
                feature=feature,
                minimum=_ZERO,
            )


@dataclass(frozen=True)
class TravelAllowanceEvent:
    """Daily travel allowance (indennità di trasferta) of a block of days.

    The allowance outside the comune is income only above the daily cap of
    art. 51 c. 5 TUIR, for IRPEF and INPS alike (art. 12 c. 2 L. 153/1969);
    within the comune it is income in full.  One event covers days with the
    same daily amount and the same conditions.  Analytic reimbursements and
    travel costs are not pay and are not events.

    Attributes:
        event_date: Date the block of days is attributed to.
        days: Days of trasferta, at least 1.
        outside_municipality: Whether the trasferta is outside the comune of
            the place of work: within it no part is exempt.
        meals_lodging: ``"one"`` when meals or lodging are reimbursed or
            provided free, ``"both"`` when both are, ``"none"`` otherwise:
            the cap is reduced by one third or by two thirds.  Required:
            ``"none"`` gives the largest exemption.
        daily_amount: Allowance paid for each day in EUR, above 0; ``None``
            takes the CCNL amount for :attr:`hours_away`.
        hours_away: Hours away of each day, read with ``daily_amount``
            ``None`` to select the CCNL span.
        tfr_base: What enters the TFR base: ``"none"``, ``"whole"``, or
            ``"above_exempt"`` (the part above the exemption); ``None``
            takes the CCNL rule, required without one.
        abroad: Whether the trasferta is abroad, with the higher cap.
        trasfertista: Whether the worker is bound by contract to work in
            places always different (art. 51 c. 6 TUIR, 50% exempt):
            not supported, the event is rejected.

    Raises:
        InvalidInputError: When a field is invalid, neither
            ``daily_amount`` nor ``hours_away`` is given, or
            ``trasfertista`` is ``True``.
    """

    event_date: date
    days: int
    outside_municipality: bool
    meals_lodging: Literal["none", "one", "both"]
    daily_amount: Decimal | None = None
    hours_away: Decimal | None = None
    tfr_base: Literal["none", "whole", "above_exempt"] | None = None
    abroad: bool = False
    trasfertista: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        feature = "travel_allowance"
        name = "TravelAllowanceEvent"
        require_date(self.event_date, f"{name}.event_date", feature=feature)
        require_int(self.days, f"{name}.days", feature=feature, minimum=1, maximum=31)
        require_decimal(
            self.daily_amount,
            f"{name}.daily_amount",
            feature=feature,
            positive=True,
            optional=True,
        )
        require_decimal(
            self.hours_away,
            f"{name}.hours_away",
            feature=feature,
            minimum=_ZERO,
            maximum=Decimal(24),
            optional=True,
        )
        if self.daily_amount is None and self.hours_away is None:
            msg = f"{name}: state daily_amount or the hours_away of the CCNL span"
            raise InvalidInputError(msg, field=f"{name}.hours_away", feature=feature)
        for flag in ("outside_municipality", "abroad", "trasfertista"):
            require_bool(getattr(self, flag), f"{name}.{flag}", feature=feature)
        require_choice(
            self.meals_lodging, _MEALS_LODGING, f"{name}.meals_lodging", feature=feature
        )
        if self.tfr_base is not None:
            require_choice(
                self.tfr_base, _TFR_BASES, f"{name}.tfr_base", feature=feature
            )
        if self.trasfertista:
            msg = (
                "TravelAllowanceEvent.trasfertista: the allowance of a worker "
                "bound to always different places is 50% income (art. 51 c. 6 "
                "TUIR), not supported; pass it as a bonus with its taxable half"
            )
            raise InvalidInputError(msg, field=f"{name}.trasfertista", feature=feature)
