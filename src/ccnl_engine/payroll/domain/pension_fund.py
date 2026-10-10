"""Enrolment of the worker in the complementary pension fund of the CCNL."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validation import (
    require_bool,
    require_date,
    require_decimal,
    require_str,
)

__all__ = [
    "PENSION_FEATURE",
    "PENSION_FUND_TYPES",
    "NoPensionFund",
    "PensionFundEnrolment",
]

#: Feature reported by the errors of the pension fund enrolment.
PENSION_FEATURE = "pension_fund"

_ZERO = Decimal(0)
_ONE = Decimal(1)


@dataclass(frozen=True, slots=True)
class PensionFundEnrolment:
    """The worker's enrolment in a pension fund of the CCNL.

    Enrolment is voluntary (D.Lgs. 252/2005 art. 1 c. 2), so it is a fact
    of the employment, never derived from the CCNL.  The employer rate and
    its base come from the fund in ``CCNL.parameters.employer_funds``.

    Attributes:
        fund_code: Code of the fund in the CCNL data, e.g. ``"ALIFOND"``.
        employee_rate: Contribution the worker chose, as a fraction of the
            same base as the employer rate, e.g. ``Decimal("0.01")``.  It
            cannot be below the minimum of the CCNL when the bundle records
            one, except zero: a worker who confers the TFR alone, with no
            contribution of either side (D.Lgs. 252/2005 art. 8 c. 1).
        tfr_to_fund: Whether the TFR accrued is paid to the fund
            (D.Lgs. 252/2005 art. 8 c. 1-2).  Required: the choice is the
            worker's, and it moves the TFR out of the company.
        young_member: Whether the worker belongs to the members the CCNL
            favours for the age at enrolment (Cometa: enrolled after 5
            February 2021 before turning 35), read only by a fund with a
            ``young_member_rate``; ``None`` when not stated.
        conventional_base: Monthly base the fund applies to the worker, read
            only by a fund on a conventional base (Previambiente: the base
            pay of the level at 1 January 1997, its contingenza and one
            scatto, e.g. 2077.84 for a quadro); ``None`` when not stated.
        seniority_to_fund: Whether the worker opted to convert the
            seniority increments into fund contributions, read only by a
            fund with a ``seniority_conversion`` (Previambiente art. 65
            lett. A) bis): not unless stated.
        seniority_converted_on: Date of the request of a worker already in
            service (lett. A) bis c. 6): the increments matured by then stay
            in the pay, frozen, and only the later ones are converted;
            ``None`` for a new hire who opted at the hire (c. 1).

    Raises:
        InvalidInputError: When a field is not of its type, ``fund_code``
            is empty, ``employee_rate`` is outside [0, 1], or zero with no
            TFR conferred.
    """

    fund_code: str
    employee_rate: Decimal
    tfr_to_fund: bool
    young_member: bool | None = None
    conventional_base: Decimal | None = None
    seniority_to_fund: bool = False
    seniority_converted_on: date | None = None

    @property
    def tfr_only(self) -> bool:
        """Whether the worker confers the TFR alone, with no contribution."""
        return self.employee_rate == 0

    def __post_init__(self) -> None:  # noqa: D105
        owner = "PensionFundEnrolment"
        require_str(
            self.fund_code,
            f"{owner}.fund_code",
            feature=PENSION_FEATURE,
            non_blank=True,
        )
        require_decimal(
            self.employee_rate,
            f"{owner}.employee_rate",
            feature=PENSION_FEATURE,
            minimum=_ZERO,
            maximum=_ONE,
        )
        require_bool(self.tfr_to_fund, f"{owner}.tfr_to_fund", feature=PENSION_FEATURE)
        if self.tfr_only and not self.tfr_to_fund:
            msg = (
                f"{owner} with employee_rate 0 confers the TFR alone: "
                "tfr_to_fund must be True"
            )
            raise InvalidInputError(msg, feature=PENSION_FEATURE)
        if self.young_member is not None:
            require_bool(
                self.young_member, f"{owner}.young_member", feature=PENSION_FEATURE
            )
        require_bool(
            self.seniority_to_fund,
            f"{owner}.seniority_to_fund",
            feature=PENSION_FEATURE,
        )
        if self.seniority_converted_on is not None:
            require_date(
                self.seniority_converted_on,
                f"{owner}.seniority_converted_on",
                feature=PENSION_FEATURE,
            )
            if not self.seniority_to_fund:
                msg = f"{owner}.seniority_converted_on needs seniority_to_fund"
                raise InvalidInputError(msg, feature=PENSION_FEATURE)
        require_decimal(
            self.conventional_base,
            f"{owner}.conventional_base",
            feature=PENSION_FEATURE,
            minimum=_ZERO,
            optional=True,
        )


@dataclass(frozen=True, slots=True)
class NoPensionFund:
    """The worker is stated not enrolled in a pension fund of the CCNL.

    It is the fact ``Employment.pension_fund`` left ``None`` does not
    state: on every CCNL but domestic work, an unknown enrolment leaves the
    contributions to the fund undetermined.  Whether the TFR of a worker
    who expressed no choice goes to the fund (D.Lgs. 252/2005 art. 8 c. 7)
    is for the caller to establish: the engine does not infer it.
    """


#: Types that state the enrolment of the worker in a fund of the CCNL.
PENSION_FUND_TYPES = (PensionFundEnrolment, NoPensionFund)
