"""Internal pay-chain value types for the computation engine."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.compensation import Allowance

_ZERO = Decimal(0)


class MonthPeriod(Protocol):
    """Structural protocol for apprenticeship period objects."""

    months_from: int
    months_until: int | None


@dataclass(frozen=True)
class MonthlyPayChain:
    """Full-time monthly pay components of one level on one date."""

    base: Decimal
    seniority: Decimal
    allowances: tuple[tuple[Allowance, Decimal], ...]

    def scaled(self, factor: Decimal) -> MonthlyPayChain:
        """Scale all components by ``factor``.

        Returns:
            A new chain with every component multiplied by ``factor``.
        """
        return MonthlyPayChain(
            base=money(self.base * factor),
            seniority=money(self.seniority * factor),
            allowances=tuple((a, money(v * factor)) for a, v in self.allowances),
        )

    def scaled_for_part_time(self, factor: Decimal) -> MonthlyPayChain:
        """Scale only proportionable components by ``factor``.

        Base salary and seniority are always proportionable.  Allowances are
        scaled only when :attr:`~ccnl_engine.engine.contract.domain.compensation\
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
        )

    @property
    def allowances_total(self) -> Decimal:
        """Rounded sum of all allowance amounts."""
        return money(sum((v for _, v in self.allowances), _ZERO))
