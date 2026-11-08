"""Worker and short-absence facts for cumulative sickness treatment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.seniority.inputs import SeniorityFact


@dataclass(frozen=True)
class SicknessWorker:
    """Facts of the worker the cumulated sickness is counted with.

    Attributes:
        seniority: Recognised seniority, ``None`` when not known.
        hired_on: First day of the employment, ``None`` when not known.
        known_from: First day from which the recorded episodes list every
            sick day of the employment; ``None`` when they list all of them.
        fixed_term: Whether the contract is fixed-term.
    """

    seniority: SeniorityFact | None = None
    hired_on: date | None = None
    known_from: date | None = None
    fixed_term: bool = False


@dataclass(frozen=True)
class ShortAbsence:
    """Rate of the first days of a short absence.

    Attributes:
        rate: The rate, ``1`` without a reduction.
        unknown: Whether an unstated exemption could change it.
    """

    rate: Decimal = Decimal(1)
    unknown: bool = False
