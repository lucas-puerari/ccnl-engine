"""Employment spells of a tax year: the days the art. 13 TUIR deduction counts.

Art. 13 c. 1 TUIR proportions the deduction "al periodo di lavoro
nell'anno".  The tax cash state of one sostituto counts the income of every
employment it paid in the tax year, a rehire after an earlier employment
included: the Certificazione Unica holds one certificate per worker "anche in
presenza di più rapporti di lavoro rilasciate dal sostituto per il medesimo
periodo d'imposta", punto 11 code 1 marks an employment "interrotto e
successivamente ripreso nel corso dell'anno", and punto 721 counts "il
numero dei giorni di lavoro dipendente totali, tenendo conto, quindi, di
tutti i rapporti di lavoro conguagliati", "i giorni compresi in periodi
contemporanei" once (Agenzia delle Entrate, istruzioni CU 2026, aggiornate
al 24 febbraio 2026).  The days of the deduction are therefore those of the
union of the spells of the income the withholding is computed on.

The lett. a) minimum is 1,380 EUR when one of those employments is
fixed-term: Allegato C to the 730/2026 instructions, par. 19.9.1, takes it
"se nella casella di colonna 2 dei righi da C1 a C3 è presente in almeno un
rigo il codice 2 (redditi di lavoro dipendente a tempo determinato)".

A spell is keyed by its first day in the year: a later run of the same
employment, which states its end, replaces the spell an earlier run
recorded open to 31 December.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING, final

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validation import require_bool, require_date
from ccnl_engine.validation_collection import items_of_type, tuple_of

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod

__all__ = ["EmploymentSpell", "spell_days", "spells_of", "spells_with"]

_FEATURE = "employment_spells"
_OWNER = "EmploymentSpell"
#: Days a tax year counts at most: the art. 13 deduction is in 365ths.
_MAX_DAYS = 365
_DAY = timedelta(days=1)


@final
@dataclass(frozen=True, slots=True)
class EmploymentSpell:
    """Days of one employment within a tax year.

    Attributes:
        first_day: First day of the employment in the year.
        last_day: Last day of the employment in the year: its end, or 31
            December while the end is not stated.
        fixed_term: Whether the employment is fixed-term.
        unpaid_days: Days of the spell for which no pay at all is due
            (aspettativa senza assegni), in order: they leave the days of the
            deductions (AdE circ. 15/E/2007 par. 1.5.1).

    Raises:
        InvalidInputError: When a field is not of its type, or the days are
            not of one year in order.
    """

    first_day: date
    last_day: date
    fixed_term: bool
    unpaid_days: tuple[date, ...] = ()

    def __post_init__(self) -> None:  # noqa: D105
        require_date(self.first_day, f"{_OWNER}.first_day", feature=_FEATURE)
        require_date(self.last_day, f"{_OWNER}.last_day", feature=_FEATURE)
        require_bool(self.fixed_term, f"{_OWNER}.fixed_term", feature=_FEATURE)
        if self.last_day < self.first_day or self.last_day.year != self.first_day.year:
            msg = (
                f"an employment spell runs within one year, first day first; "
                f"got {self.first_day} to {self.last_day}"
            )
            raise InvalidInputError(msg, field=_OWNER, feature=_FEATURE)
        days = tuple_of(
            self.unpaid_days,
            f"{_OWNER}.unpaid_days",
            items_of_type(date, feature=_FEATURE),
            feature=_FEATURE,
        )
        inside = all(self.first_day <= d <= self.last_day for d in days)
        if list(days) != sorted(set(days)) or not inside:
            msg = "unpaid days are distinct days of the spell, in order"
            raise InvalidInputError(
                msg, field=f"{_OWNER}.unpaid_days", feature=_FEATURE
            )
        object.__setattr__(self, "unpaid_days", days)

    def with_unpaid(self, days: Iterable[date]) -> EmploymentSpell:
        """Return the spell with ``days`` added to its unpaid days.

        Returns:
            The spell with the days of ``days`` that fall within it.
        """
        inside = {d for d in days if self.first_day <= d <= self.last_day}
        merged = tuple(sorted(inside | set(self.unpaid_days)))
        return EmploymentSpell(self.first_day, self.last_day, self.fixed_term, merged)

    @classmethod
    def of(
        cls, period: EmploymentPeriod | None, year: int, *, fixed_term: bool
    ) -> EmploymentSpell | None:
        """Return the spell of ``period`` in ``year``.

        Args:
            period: The employment period; ``None`` when its start is not
                stated, which covers the whole year.
            year: The tax year.
            fixed_term: Whether the employment is fixed-term.

        Returns:
            The spell, or ``None`` when the period has no day in ``year``.
        """
        first, last = date(year, 1, 1), date(year, 12, 31)
        if period is not None:
            first = max(first, period.started_on)
            if period.ended_on is not None:
                last = min(last, period.ended_on)
        if last < first:
            return None
        return cls(first, last, fixed_term)


def spells_of(
    value: object, path: str, tax_year: int | None
) -> tuple[EmploymentSpell, ...]:
    """Return the validated spells of a tax year.

    Args:
        value: The spells, a tuple or a list.
        path: The field the spells are read from, for the errors.
        tax_year: The tax year the spells must belong to; ``None`` on a
            state not bound to a year, which holds none.

    Returns:
        The spells as a tuple.

    Raises:
        InvalidInputError: When an item is not a spell, the spells are not
            in order of distinct first days, or one is of another year.
    """
    spells = tuple_of(
        value, path, items_of_type(EmploymentSpell, feature=_FEATURE), feature=_FEATURE
    )
    firsts = [s.first_day for s in spells]
    if firsts != sorted(set(firsts)):
        msg = f"spells must have distinct first days, in order; got {firsts}"
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    if any(s.first_day.year != tax_year for s in spells):
        msg = f"every spell must be of the tax year {tax_year}"
        raise InvalidInputError(msg, field=path, feature=_FEATURE)
    return spells


def spells_with(
    spells: tuple[EmploymentSpell, ...], spell: EmploymentSpell | None
) -> tuple[EmploymentSpell, ...]:
    """Return ``spells`` with ``spell`` in place of the one of its first day.

    Returns:
        The spells in order of first day; ``spells`` when ``spell`` is
        ``None``.
    """
    if spell is None:
        return spells
    others = [s for s in spells if s.first_day != spell.first_day]
    return tuple(sorted((*others, spell), key=lambda s: s.first_day))


def spell_days(spells: tuple[EmploymentSpell, ...]) -> int:
    """Return the paid days of the union of ``spells``, at most 365.

    Days in two spells count once (CU 2026, punto 721); a day leaves the
    count when no spell that covers it pays it (AdE circ. 15/E/2007 par.
    1.5.1); a leap year counts at most 365, the denominator of the art. 13
    TUIR proportion.

    Returns:
        The calendar days for which at least one spell pays.
    """
    paid: set[date] = set()
    for spell in spells:
        unpaid = set(spell.unpaid_days)
        count = (spell.last_day - spell.first_day).days + 1
        days = (spell.first_day + _DAY * n for n in range(count))
        paid.update(d for d in days if d not in unpaid)
    return min(len(paid), _MAX_DAYS)
