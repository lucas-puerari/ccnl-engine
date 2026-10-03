"""Internal pay-chain value types for the computation engine."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.compensation import Allowance

_ZERO = Decimal(0)


class MonthPeriod(Protocol):
    """Structural protocol for apprenticeship period objects."""

    months_from: int
    months_until: int | None


@dataclass(frozen=True)
class MonthlyPayChain:
    """Full-time monthly pay components of one level on one date.

    ``limitations`` holds the ids of the engine limitations whose code path
    built the chain; every derived chain keeps them.
    """

    base: Decimal
    seniority: Decimal
    allowances: tuple[tuple[Allowance, Decimal], ...]
    limitations: tuple[str, ...] = ()

    def scaled(self, factor: Decimal) -> MonthlyPayChain:
        """Scale all components by ``factor``.

        Returns:
            A new chain with every component multiplied by ``factor``.
        """
        return MonthlyPayChain(
            base=money(self.base * factor),
            seniority=money(self.seniority * factor),
            allowances=tuple((a, money(v * factor)) for a, v in self.allowances),
            limitations=self.limitations,
        )

    def scaled_for_apprenticeship(self, percentage: Decimal) -> MonthlyPayChain:
        """Scale the components a percentage apprenticeship reduces.

        Base salary and seniority are always reduced.  Allowances are
        reduced only when :attr:`~ccnl_engine.contract.domain.compensation\
.Allowance.apprenticeship_pct_relevant` is ``True``; the others are paid
        at their full contractual value.

        Returns:
            A new chain with selectively scaled components.
        """
        return MonthlyPayChain(
            base=money(self.base * percentage),
            seniority=money(self.seniority * percentage),
            allowances=tuple(
                (a, money(v * percentage) if a.apprenticeship_pct_relevant else v)
                for a, v in self.allowances
            ),
            limitations=self.limitations,
        )

    def scaled_for_part_time(self, factor: Decimal) -> MonthlyPayChain:
        """Scale only proportionable components by ``factor``.

        Base salary and seniority are always proportionable.  Allowances are
        scaled only when :attr:`~ccnl_engine.contract.domain.compensation\
.Allowance.part_time_proportionable` is ``True``; allowances with
        ``part_time_proportionable=False`` retain their full contractual value.

        Returns:
            A new chain with selectively scaled components.
        """
        return MonthlyPayChain(
            base=money(self.base * factor),
            seniority=money(self.seniority * factor),
            allowances=tuple(
                (a, money(v * factor) if a.part_time_proportionable else v)
                for a, v in self.allowances
            ),
            limitations=self.limitations,
        )

    def for_extra_month(self, months_threshold: int) -> MonthlyPayChain:
        """Return a chain containing only allowances eligible for an extra-month run.

        An allowance is included when its ``months_per_year`` is ``None``
        (no restriction) or is at least ``months_threshold``.  Allowances
        paid fewer than ``months_threshold`` times per year (e.g. an EDR paid
        only 12 times in a 13-month contract) are excluded from the run.
        Base salary and seniority are always included.

        Args:
            months_threshold: Minimum ``months_per_year`` for inclusion.
                Pass the CCNL ``additional_months`` value (13 for tredicesima,
                14 for quattordicesima).

        Returns:
            A filtered :class:`MonthlyPayChain`.
        """
        eligible = tuple(
            (a, v)
            for a, v in self.allowances
            if a.months_per_year is None or a.months_per_year >= months_threshold
        )
        return MonthlyPayChain(
            base=self.base,
            seniority=self.seniority,
            allowances=eligible,
            limitations=self.limitations,
        )

    @property
    def allowances_total(self) -> Decimal:
        """Rounded sum of all allowance amounts."""
        return money(sum((v for _, v in self.allowances), _ZERO))


@dataclass(frozen=True)
class ApprenticeshipScaling:
    """Percentage applied to an apprentice's pay chain and what it reduced.

    Attributes:
        percentage: Share of the reference pay due in the current period.
        scaled: Components reduced to ``percentage``: ``base_salary``,
            ``seniority`` when due, then the codes of the allowances whose
            ``apprenticeship_pct_relevant`` is true.
        unscaled: Codes of the allowances paid at full value.
    """

    percentage: Decimal
    scaled: tuple[str, ...]
    unscaled: tuple[str, ...]

    @classmethod
    def of(cls, chain: MonthlyPayChain, percentage: Decimal) -> ApprenticeshipScaling:
        """Describe which components of ``chain`` the percentage reduces.

        Mirrors :meth:`MonthlyPayChain.scaled_for_apprenticeship`.

        Args:
            chain: Full-value pay chain of the reference level.
            percentage: Apprenticeship percentage of the current period.

        Returns:
            The percentage with the scaled and unscaled component codes.
        """
        fixed = ("base_salary", "seniority") if chain.seniority else ("base_salary",)
        relevant = tuple(
            a.code for a, _ in chain.allowances if a.apprenticeship_pct_relevant
        )
        exempt = tuple(
            a.code for a, _ in chain.allowances if not a.apprenticeship_pct_relevant
        )
        return cls(percentage=percentage, scaled=fixed + relevant, unscaled=exempt)
