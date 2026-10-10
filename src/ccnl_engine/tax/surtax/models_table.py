"""Surtax table value objects: the rates and deductions of one jurisdiction.

A regional entry (:class:`RegionaleEntry`) or a municipal entry
(:class:`ComunaleEntry`) holds the brackets, exemptions and deductions of a
single region or municipality for one tax year; the tables keyed by
jurisdiction live in :mod:`~ccnl_engine.tax.surtax.models`.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.primitives import Bracket
from ccnl_engine.provenance.source.models_chain import RuleProvenance

#: One marginal bracket in a surtax rate schedule.
#: Shares the same structure as :class:`~ccnl_engine.tax.models.IrpefBracket`
#: so the same bracket-sum computation can be reused.
SurtaxBracket = Bracket


def _validate_surtax_brackets(brackets: Sequence[SurtaxBracket], label: str) -> None:
    """Validate that *brackets* form a well-ordered marginal rate schedule.

    Rules (mirrors ``YearRulesRaw._check_irpef_brackets``):
    - The list must not be empty.
    - Only the last bracket may have ``up_to=None``.
    - ``up_to`` values in non-final brackets must be strictly ascending.

    Raises:
        ValueError: If any rule is violated.
    """
    if not brackets:
        msg = f"{label}.brackets must not be empty"
        raise ValueError(msg)
    for i, b in enumerate(brackets[:-1]):
        if b.up_to is None:
            msg = (
                f"{label}: only the last bracket may have up_to=None "
                f"(bracket {i} of {len(brackets)} is not the last)"
            )
            raise ValueError(msg)
        next_b = brackets[i + 1]
        if next_b.up_to is not None and next_b.up_to <= b.up_to:
            msg = (
                f"{label}: brackets must have strictly ascending up_to; "
                f"bracket {i} up_to={b.up_to} >= bracket {i + 1} up_to={next_b.up_to}"
            )
            raise ValueError(msg)
    if brackets[-1].up_to is not None:
        msg = (
            f"{label}: last bracket must be unbounded (up_to=None), "
            f"got up_to={brackets[-1].up_to}"
        )
        raise ValueError(msg)


class WholeIncomeRate(BaseModel):
    """One rate on the whole income for incomes up to a limit.

    Some regions replace the marginal brackets with a single rate on the
    whole taxable income when that income does not exceed a limit (e.g.
    Lazio 2026: 1.73% up to 28,000 euro).  Above the limit the marginal
    brackets of the entry apply.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    income_up_to: Decimal = Field(gt=0)
    """Largest taxable income the rate applies to, inclusive."""
    rate: Decimal = Field(ge=0, le=1)
    """Rate on the whole taxable income, as a decimal (0.0173 = 1.73%)."""


class RegionalDeduction(BaseModel):
    """A detrazione from the regional surtax that depends on income only.

    The deduction is due when ``income_above < taxable income`` and, if
    ``income_up_to`` is set, ``taxable income <= income_up_to``.  With
    ``phase_in`` the amount grows linearly from zero at ``income_above`` to
    ``amount`` at ``income_above + phase_in``.  Deductions never create a
    credit: the surtax net of them is floored at zero.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    amount: Decimal = Field(gt=0)
    """Full annual deduction in euro."""
    income_above: Decimal = Field(default=Decimal(0), ge=0)
    """Taxable income the deduction starts above, exclusive."""
    income_up_to: Decimal | None = None
    """Largest taxable income the deduction applies to, inclusive."""
    phase_in: Decimal | None = Field(default=None, gt=0)
    """Income width over which the amount grows from zero to ``amount``."""

    @model_validator(mode="after")
    def _check_band(self) -> Self:
        if self.income_up_to is not None and self.income_up_to <= self.income_above:
            msg = (
                "RegionalDeduction: income_up_to must exceed income_above, got "
                f"{self.income_up_to} <= {self.income_above}"
            )
            raise ValueError(msg)
        return self


class RegionaleEntry(BaseModel):
    """Addizionale regionale IRPEF for one region/autonomous province.

    ``brackets`` always has at least one element. Regions with a single
    flat rate have exactly one bracket with ``up_to=None``.

    The income-only provisions of the regional law are modelled:
    ``exemption_threshold``, ``whole_income_rate`` and ``deductions``.
    Provisions that depend on dependents or on disability (per-child
    deductions, reduced rates for families with a disabled member) are not
    computed; ``dependent_provisions`` states them so the engine can flag a
    result whose worker may be entitled to them.

    The model is frozen: field values cannot be reassigned after construction.
    ``brackets`` is a tuple so the collection itself is immutable.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    brackets: tuple[SurtaxBracket, ...]
    """Marginal rate brackets, ascending by ``up_to`` with the last entry unbounded."""

    exemption_threshold: Decimal = Field(default=Decimal(0), ge=0)
    """Exemption threshold: if taxable income <= threshold, the surtax is zero."""
    whole_income_rate: WholeIncomeRate | None = None
    """Rate on the whole income that replaces the brackets up to a limit."""
    deductions: tuple[RegionalDeduction, ...] = ()
    """Income-only detrazioni, subtracted from the surtax and floored at zero."""
    dependent_provisions: str | None = None
    """Provisions for dependents or disability that the engine does not apply."""
    notes: str = ""
    """Free-form note (e.g. reference to the regional law)."""
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_brackets(self) -> Self:
        _validate_surtax_brackets(self.brackets, "RegionaleEntry")
        return self


class ComunaleDeduction(BaseModel):
    """Optional deduction subtracted from the computed comunale surtax.

    ``fixed`` is subtracted unconditionally; ``per_dependent`` is multiplied
    by the number of dependents before subtracting.  Both default to zero.
    The net surtax is floored at zero after deductions.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    fixed: Decimal = Decimal(0)
    """Fixed annual deduction from the computed surtax."""
    per_dependent: Decimal = Decimal(0)
    """Additional deduction per dependent (multiplied by dependent count)."""


class WithholdingCalendar(BaseModel):
    """Informational model describing when surtax installments are withheld.

    This model describes the withholding schedule for employer-withheld surtax
    installments.  It does not affect the computed annual amount; the engine
    always computes the annual figure.  Period-level monthly distribution is
    out of scope for this model.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    advance_month: int = 11
    """Month (1-12) in which the advance (acconto) installment is withheld."""
    balance_installments: int = 11
    """Number of equal installments for the balance (saldo), starting March."""


class ComunaleEntry(BaseModel):
    """Addizionale comunale IRPEF for one municipality.

    Municipalities with a simple flat rate have exactly one bracket with
    ``up_to=None`` and ``exemption_threshold=0``. Municipalities with income
    brackets or an exemption threshold will have multiple brackets and/or
    ``exemption_threshold > 0``.

    The model is frozen: field values cannot be reassigned after construction.
    ``brackets`` is a tuple so the collection itself is immutable.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    nome: str
    """Italian municipality name (e.g. ``"Roma"``)."""

    brackets: tuple[SurtaxBracket, ...]
    """Marginal rate brackets, ascending by ``up_to`` with the last entry unbounded."""

    exemption_threshold: Decimal = Decimal(0)
    """Exemption threshold: if taxable income ≤ threshold, the surtax is zero."""
    deduction: ComunaleDeduction = Field(default_factory=ComunaleDeduction)
    """Optional fixed or per-dependent deduction from the computed surtax."""
    safeguard_clause: Decimal | None = None
    """Max increase from prior year (clausola di salvaguardia); not computable
    without prior-year taxable income — present as data only."""
    withholding_calendar: WithholdingCalendar = Field(
        default_factory=WithholdingCalendar
    )
    """Informational withholding schedule for this municipality."""
    rates_year: int | None = None
    """Year of the delibera the rates come from; ``None`` for the table year.

    A year before the table year means no delibera of the table year was
    published and the rates of that year are carried forward (art. 1 c. 169
    L. 296/2006).
    """
    specific_exemptions: tuple[str, ...] = ()
    """Exemptions for a category of income only (e.g. lavoro dipendente up
    to a limit), as published; not computed by the engine."""
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_brackets(self) -> Self:
        _validate_surtax_brackets(self.brackets, "ComunaleEntry")
        return self
