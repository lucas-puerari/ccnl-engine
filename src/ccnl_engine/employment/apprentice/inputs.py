"""Apprenticeship contract, whose pay the CCNL apprenticeship rules derive."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from ccnl_engine.validators import (
    parse_enum,
    require_decimal,
    require_instance,
    require_int,
    require_str,
)

__all__ = ["Apprentice", "ApprenticeshipProgramme", "DualHours"]

_CONTRACT_FEATURE = "contract_type"
_ZERO = Decimal(0)


class ApprenticeshipProgramme(StrEnum):
    """Kind of apprenticeship (D.Lgs. 81/2015 artt. 43-45).

    Attributes:
        PROFESSIONALISING: Apprendistato professionalizzante (art. 44).
        FIRST_LEVEL: Apprendistato per la qualifica e il diploma
            professionale, il diploma di istruzione secondaria superiore e
            il certificato di specializzazione tecnica superiore (art. 43).
        THIRD_LEVEL: Apprendistato di alta formazione e di ricerca (art. 45).
    """

    PROFESSIONALISING = "professionalising"
    FIRST_LEVEL = "first_level"
    THIRD_LEVEL = "third_level"


@dataclass(frozen=True, slots=True)
class DualHours:
    """Hours of a first- or third-level apprentice over a stretch of time.

    The pay of the stretch weighs each kind of hour by its share of the
    total (D.Lgs. 81/2015 art. 43 c. 7, art. 45 c. 3).

    Attributes:
        school: Hours of training in the educational institution, which
            the employer does not pay.
        company_training: Hours of training the employer provides.
        work: Hours of work at the employer.

    Raises:
        InvalidInputError: When an hour count is negative, or all are 0.
    """

    school: Decimal
    company_training: Decimal
    work: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("school", "company_training", "work"):
            require_decimal(
                getattr(self, name),
                f"DualHours.{name}",
                feature=_CONTRACT_FEATURE,
                minimum=_ZERO,
            )
        require_decimal(
            self.total,
            "DualHours total",
            feature=_CONTRACT_FEATURE,
            positive=True,
        )

    @property
    def total(self) -> Decimal:
        """Hours of the three kinds together."""
        return self.school + self.company_training + self.work


@dataclass(frozen=True, slots=True)
class Apprentice:
    """Apprenticeship contract; salary is derived from CCNL apprenticeship rules.

    Attributes:
        months_elapsed: Months of apprenticeship service elapsed so far,
            ``>= 0``.  Used to look up the applicable ``apprenticeship_pct``
            in the CCNL percentage track, or the under-classification level
            in under-classification tracks.
        track: Name of the CCNL apprenticeship track to apply. Required
            only when more than one track covers the destination level;
            ``None`` lets the engine select the unique applicable track.
        programme: Kind of apprenticeship; a first- or third-level one
            is paid by the CCNL ``dual_apprenticeship`` tracks.
        school_year: Year of the school or training course the apprentice
            attends, for a CCNL that pays a first-level apprentice by it;
            ``None`` when not stated.
        programme_months: Length in months of the whole apprenticeship,
            for a CCNL that pays by the half of the programme or by its
            length; ``None`` when not stated.
        hours: Hours of the month by kind, for a first- or third-level
            apprentice; on an extra-month or final-settlement run, the
            hours of the period the ratei accrue over.  ``None`` when not
            stated.

    Raises:
        InvalidInputError: When a field has the wrong type or range.
    """

    months_elapsed: int
    track: str | None = None
    programme: ApprenticeshipProgramme = ApprenticeshipProgramme.PROFESSIONALISING
    school_year: int | None = None
    programme_months: int | None = None
    hours: DualHours | None = None
    type: Literal["apprentice"] = field(default="apprentice", init=False)

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.months_elapsed,
            "Apprentice.months_elapsed",
            feature=_CONTRACT_FEATURE,
            minimum=0,
        )
        require_str(
            self.track,
            "Apprentice.track",
            feature=_CONTRACT_FEATURE,
            non_blank=True,
            optional=True,
        )
        object.__setattr__(
            self,
            "programme",
            parse_enum(
                self.programme,
                ApprenticeshipProgramme,
                "Apprentice.programme",
                feature=_CONTRACT_FEATURE,
            ),
        )
        for name in ("school_year", "programme_months"):
            require_int(
                getattr(self, name),
                f"Apprentice.{name}",
                feature=_CONTRACT_FEATURE,
                minimum=1,
                optional=True,
            )
        require_instance(
            self.hours,
            DualHours,
            "Apprentice.hours",
            feature=_CONTRACT_FEATURE,
            optional=True,
        )
