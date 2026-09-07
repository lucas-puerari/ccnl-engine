"""Internal pay-chain value types for the computation engine."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import Allowance

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

    def scaled_selective(
        self, base_factor: Decimal, apprenticeship_pct: Decimal
    ) -> MonthlyPayChain:
        """Scale for a percentage-based apprentice.

        ``base_factor`` (part-time fraction) applies to every component.
        ``apprenticeship_pct`` additionally applies to all components
        *except* allowances whose ``apprenticeship_pct_relevant`` flag is
        ``False`` — those are paid at their full part-time value.

        Returns:
            A new chain with selectively scaled components.
        """
        combined = base_factor * apprenticeship_pct

        def _scale(a: Allowance, v: Decimal) -> Decimal:
            f = combined if a.apprenticeship_pct_relevant else base_factor
            return money(v * f)

        return MonthlyPayChain(
            base=money(self.base * combined),
            seniority=money(self.seniority * combined),
            allowances=tuple((a, _scale(a, v)) for a, v in self.allowances),
        )

    @property
    def allowances_total(self) -> Decimal:
        """Rounded sum of all allowance amounts."""
        return money(sum((v for _, v in self.allowances), _ZERO))


@dataclass(frozen=True)
class AnnualisedPay:
    """Annualised pay with gross and contribution/TFR exclusion totals."""

    gross: Decimal
    excluded_from_contributions: Decimal
    excluded_from_tfr: Decimal
