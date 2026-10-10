"""Fixed-term contract and the facts of its NASpI surcharge.

L. 92/2012 art. 2 c. 28 charges the employer of a fixed-term worker an
additional NASpI contribution of 1.4% of the INPS base, raised by 0.5
points at each renewal of the contract (period added by D.L. 87/2018
art. 3 c. 2).  C. 29 lists the contracts the surcharge does not apply to;
whether one of them applies, and how many renewals the contract follows,
are facts of the contract the caller states.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

from ccnl_engine.validation import parse_enum, require_int

__all__ = ["FixedTerm", "NaspiExclusion"]

_FEATURE = "contract_type"


class NaspiExclusion(StrEnum):
    """Why the NASpI surcharge of a fixed-term contract is not charged.

    Sources: L. 92/2012 art. 2 c. 28-29 and D.L. 87/2018 art. 1 c. 3, text
    in force on Normattiva on 7 October 2026; INPS circ. 121/2019 par. 2.2
    and 2.4.  Apprentices (c. 29 lett. c) are not a reason here: an
    apprenticeship is an :class:`~ccnl_engine.payroll.employment.inputs\
.Apprentice` contract, which never pays the surcharge.  Operai agricoli
    (c. 3) are not a reason either: the bundle marks the categories of the
    sector the whole article does not apply to.

    Attributes:
        NONE: No exclusion: the surcharge and its renewal increase apply.
        REPLACEMENT: Hired to replace absent workers (c. 29 lett. a).
        SEASONAL: Hired for the seasonal activities of DPR 1525/1963, or
            for those of the CCNLs of the provincia di Bolzano signed by 31
            December 2019 (c. 29 lett. b and b-bis).
        PUBLIC_ADMINISTRATION: Employed by a public administration of
            art. 1 c. 2 D.Lgs. 165/2001 (c. 29 lett. d).
        SHORT_SERVICE: Special services of at most three days in tourism
            and public establishments, D.Lgs. 81/2015 art. 29 c. 2 lett. b
            (c. 29 lett. d-bis).
        RESEARCH: Teaching or research at a private university, a public
            research institute, a public company promoting research or a
            private research body: the 1.4% applies, the renewal increase
            does not (D.L. 87/2018 art. 1 c. 3).
    """

    NONE = "none"
    REPLACEMENT = "replacement"
    SEASONAL = "seasonal"
    PUBLIC_ADMINISTRATION = "public_administration"
    SHORT_SERVICE = "short_service"
    RESEARCH = "research"

    @property
    def excludes_surcharge(self) -> bool:
        """Whether the whole surcharge of c. 28 is not charged."""
        return self not in {NaspiExclusion.NONE, NaspiExclusion.RESEARCH}

    @property
    def excludes_renewal_increase(self) -> bool:
        """Whether the 0.5-point increase per renewal is not charged."""
        return self is not NaspiExclusion.NONE


@dataclass(frozen=True, slots=True)
class FixedTerm:
    """Fixed-term contract, which may owe the NASpI surcharge.

    Attributes:
        renewals: Renewals of the fixed-term contract with the same
            employer, this contract being the last, signed from 14 July
            2018 (INPS circ. 121/2019 par. 2.3: earlier renewals are not
            counted).  A prorogation of the term is not a renewal.  Each
            renewal raises the surcharge by 0.5 points.  ``None`` means
            not known: a run that owes the increase has a ``missing_fact``
            blocker.
        naspi_exclusion: The exclusion of c. 29 the contract falls in,
            :attr:`NaspiExclusion.NONE` when none.  ``None`` means not
            known: a run whose sector charges the surcharge has a
            ``missing_fact`` blocker.

    Raises:
        InvalidInputError: When ``renewals`` is not a non-negative int or
            ``naspi_exclusion`` names no exclusion.
    """

    renewals: int | None = None
    naspi_exclusion: NaspiExclusion | None = None
    type: Literal["fixed_term"] = field(default="fixed_term", init=False)

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.renewals,
            "FixedTerm.renewals",
            feature=_FEATURE,
            minimum=0,
            optional=True,
        )
        if self.naspi_exclusion is not None:
            exclusion = parse_enum(
                self.naspi_exclusion,
                NaspiExclusion,
                "FixedTerm.naspi_exclusion",
                feature=_FEATURE,
            )
            object.__setattr__(self, "naspi_exclusion", exclusion)
