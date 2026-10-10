"""Family domain models for Art. 12 TUIR deductions."""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validation import (
    parse_enum,
    require_bool,
    require_date,
    require_decimal,
)
from ccnl_engine.validation_collection import items_of_type, tuple_of

_FEATURE = "family_deductions"
_ZERO = Decimal(0)
_HUNDRED = Decimal(100)


class DependentRelationship(StrEnum):
    """Relationship category of a fiscally dependent family member."""

    SPOUSE = "spouse"
    CHILD = "child"
    ASCENDANT = "ascendant"


@dataclass(frozen=True, slots=True)
class Dependent:
    """One fiscally dependent family member for Art. 12 TUIR purposes.

    The caller declares the dependent and the dated interval in which the
    conditions it cannot verify hold (marriage, cohabitation, residency,
    custody); the engine derives from it, month by month, the months the
    deduction is due (art. 12 c. 3: "rapportate a mese e competono dal mese
    in cui si sono verificate a quello in cui sono cessate le condizioni
    richieste") and, for a child, the months of the age band.

    A condition left ``None`` is unknown, never met by default: when the
    dependant would give right to a deduction in some month, the family
    deductions of the run are not determined and the run has a
    ``missing_fact`` blocker naming the field.  A condition is read only
    where art. 12 makes it one: ``own_income`` and
    ``residency_eligibility`` for every dependant (c. 2 and c. 2-bis refer
    to every deduction of c. 1), ``cohabiting`` for an ascendant (c. 1
    lett. d), ``allocation_pct`` for a child and an ascendant (lett. c and
    lett. d share the deduction; the spouse deduction of lett. a is not
    shared).  The dependency interval has no default: ``None`` is an open
    end the caller states.

    Attributes:
        relationship: Relationship to the worker.
        birth_date: Date of birth.  Required for a child: the age band of
            lett. c is evaluated in every month.  Ignored for a spouse or an
            ascendant.
        disabled: ``True`` when a disability is certified under art. 3
            L. 104/1992; a child keeps the deduction from the age of 30.
        own_income: Dependent's own reddito complessivo of the year (EUR),
            checked against the limit of art. 12 c. 2; ``None`` is unknown.
        allocation_pct: Percentage of the deduction allocated to this worker
            (0-100): the share between the parents of lett. c, or the pro
            quota share of lett. d.  ``None`` is unknown for a child or an
            ascendant; a spouse takes the whole deduction, so only ``None``
            or 100 is accepted for one.
        cohabiting: ``True`` when the ascendant lives with the worker
            (Art. 12 c. 1 lett. d post L. 207/2024); ``None`` is unknown.
            Not read for a spouse or a child.
        residency_eligibility: ``True`` when the condition of Art. 12
            c. 2-bis is met: the worker is an Italian, EU or EEA citizen, or
            the dependant is not resident abroad.  Caller-declared, not
            engine-verified; ``None`` is unknown.
        dependent_from: First day the conditions hold; ``None`` states
            that they held before the tax year.  Keyword only, required.
        dependent_until: Last day the conditions hold; ``None`` states
            that they have not ceased.  Keyword only, required.

    Raises:
        InvalidInputError: When a field is not of its type or is outside its
            range, a child has no birth date, a spouse is allocated less
            than the whole deduction, or the interval ends before it starts.
    """

    relationship: DependentRelationship
    birth_date: date | None = None
    disabled: bool = False
    own_income: Decimal | None = None
    allocation_pct: Decimal | None = None
    cohabiting: bool | None = None
    residency_eligibility: bool | None = None
    _: KW_ONLY
    dependent_from: date | None
    dependent_until: date | None

    def __post_init__(self) -> None:  # noqa: D105
        relationship = parse_enum(
            self.relationship,
            DependentRelationship,
            "Dependent.relationship",
            feature=_FEATURE,
        )
        object.__setattr__(self, "relationship", relationship)
        for name in ("birth_date", "dependent_from", "dependent_until"):
            require_date(
                getattr(self, name),
                f"Dependent.{name}",
                feature=_FEATURE,
                optional=True,
            )
        require_bool(self.disabled, "Dependent.disabled", feature=_FEATURE)
        for name in ("cohabiting", "residency_eligibility"):
            value = getattr(self, name)
            if value is not None:
                require_bool(value, f"Dependent.{name}", feature=_FEATURE)
        require_decimal(
            self.own_income,
            "Dependent.own_income",
            feature=_FEATURE,
            minimum=_ZERO,
            optional=True,
        )
        require_decimal(
            self.allocation_pct,
            "Dependent.allocation_pct",
            feature=_FEATURE,
            minimum=_ZERO,
            maximum=_HUNDRED,
            optional=True,
        )
        self._check_spouse_share()
        self._check_dates()

    def _check_spouse_share(self) -> None:
        spouse = self.relationship is DependentRelationship.SPOUSE
        share = self.allocation_pct
        if spouse and share is not None and share != _HUNDRED:
            msg = (
                "the spouse deduction of art. 12 c. 1 lett. a TUIR is not "
                f"shared: allocation_pct must be None or 100; got {share}"
            )
            raise InvalidInputError(
                msg, field="Dependent.allocation_pct", feature=_FEATURE
            )

    @property
    def share(self) -> Decimal:
        """Percentage of the deduction to this worker; 100 when not stated.

        A child or an ascendant without a stated share has a missing fact
        (:attr:`missing_facts`) and no deduction, so the 100 is never
        applied to one.
        """
        return _HUNDRED if self.allocation_pct is None else self.allocation_pct

    @property
    def missing_facts(self) -> tuple[str, ...]:
        """Conditions of art. 12 this dependant leaves unknown.

        Returns:
            The names of the fields left ``None`` that art. 12 reads for
            the relationship, in field order.
        """
        kind = self.relationship
        read = {
            "own_income": True,
            "allocation_pct": kind is not DependentRelationship.SPOUSE,
            "cohabiting": kind is DependentRelationship.ASCENDANT,
            "residency_eligibility": True,
        }
        return tuple(
            name
            for name, needed in read.items()
            if needed and getattr(self, name) is None
        )

    def may_qualify(self, income_limit: Decimal) -> bool:
        """Return whether no stated condition excludes the deduction.

        An unknown condition does not exclude it: the dependant may
        qualify once the fact is stated.

        Args:
            income_limit: Own-income limit of art. 12 c. 2 for this
                dependant.

        Returns:
            ``False`` when residency or, for an ascendant, cohabitation is
            stated as not met, or the stated own income exceeds the limit.
        """
        cohabits = (
            self.relationship is not DependentRelationship.ASCENDANT
            or self.cohabiting is not False
        )
        within = self.own_income is None or self.own_income <= income_limit
        return self.residency_eligibility is not False and cohabits and within

    def _check_dates(self) -> None:
        child = self.relationship is DependentRelationship.CHILD
        if child and self.birth_date is None:
            msg = "a child needs its birth_date: the age band is checked every month"
            raise InvalidInputError(msg, field="Dependent.birth_date", feature=_FEATURE)
        start, end = self.dependent_from, self.dependent_until
        if start is not None and end is not None and end < start:
            msg = f"dependent_until {end} is before dependent_from {start}"
            raise InvalidInputError(
                msg, field="Dependent.dependent_until", feature=_FEATURE
            )

    def dependency_months(self, year: int) -> frozenset[int]:
        """Return the months of ``year`` the conditions hold on some day.

        Returns:
            Months 1-12 the interval touches, both ends included (c. 3).
        """
        start, end = self.dependent_from, self.dependent_until
        first = 1 if start is None else _month_index(start, year)
        last = 12 if end is None else _month_index(end, year)
        return frozenset(range(max(first, 1), min(last, 12) + 1))


def _month_index(day: date, year: int) -> int:
    """Return the month of ``day`` counted from January of ``year`` as 1.

    Returns:
        ``0`` or less before ``year``, ``13`` or more after it.
    """
    return (day.year - year) * 12 + day.month


@dataclass(frozen=True, slots=True)
class FamilyComposition:
    """Caller-supplied family unit for Art. 12 TUIR deductions.

    Used to compute the family deductions the employer applies as
    *sostituto d'imposta*, on the reddito complessivo of
    :class:`~ccnl_engine.payroll.domain.current_year.CurrentYearTaxFacts`.
    Eligibility conditions the engine cannot verify (residency, disability
    certification, the dependents' own income) are taken as declared; one
    left unknown grants no deduction (see :class:`Dependent`).  The children
    also select the fringe-benefit threshold (L. 207/2024 art. 1 c. 390).

    Attributes:
        dependents: The dependents; a list is accepted and stored as a
            tuple.
        sole_parent: ``True`` when the other parent is missing or has not
            recognized the children, or the children are the worker's
            alone, and the worker is not married or is legally separated:
            for the first child the spouse deduction of lett. a applies
            when more favourable (art. 12 c. 1 lett. c, last period).
    """

    dependents: tuple[Dependent, ...] = ()
    sole_parent: bool = False

    def __post_init__(self) -> None:
        """Validate every dependent and accept at most one spouse.

        Raises:
            InvalidInputError: When a dependent is not a :class:`Dependent`,
                more than one is a spouse, or a sole parent declares a
                spouse.
        """
        require_bool(
            self.sole_parent, "FamilyComposition.sole_parent", feature=_FEATURE
        )
        dependents = tuple_of(
            self.dependents,
            "FamilyComposition.dependents",
            items_of_type(Dependent, feature=_FEATURE),
            feature=_FEATURE,
        )
        object.__setattr__(self, "dependents", dependents)
        spouses = [
            d for d in dependents if d.relationship == DependentRelationship.SPOUSE
        ]
        if len(spouses) > 1:
            msg = f"FamilyComposition accepts at most one spouse; got {len(spouses)}"
            raise InvalidInputError(
                msg, field="FamilyComposition.dependents", feature=_FEATURE
            )
        if spouses and self.sole_parent:
            msg = "a sole parent declares no spouse (art. 12 c. 1 lett. c)"
            raise InvalidInputError(
                msg, field="FamilyComposition.sole_parent", feature=_FEATURE
            )

    @property
    def has_any_dependent(self) -> bool:
        """True when at least one dependent is declared."""
        return bool(self.dependents)
