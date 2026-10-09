"""Calculation status, issues and decisions attached to payroll results.

A result is only as trustworthy as its weakest input.  Each capability that
cannot fully decide (an unknown table, a missing fact, an unsupported case)
records a :class:`CalculationIssue`; the calculation axis of the result
assurance is the worst status implied by its issues and decisions.  A
:class:`CalculationDecision` records what one capability actually decided,
from which normalized inputs and under which rule version.  Its
:class:`DecisionOrigin` tells a rule the engine applied from the bundle or
the law from a value the caller supplied in its place.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.shared.domain.primitives import FrozenDict

if TYPE_CHECKING:
    from collections.abc import Iterable
    from decimal import Decimal

    from ccnl_engine.provenance.domain.source import SourceLocation

__all__ = [
    "PUBLIC_FACTS",
    "CalculationDecision",
    "CalculationIssue",
    "CalculationStatus",
    "DecisionOrigin",
]

_CODE_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


class CalculationStatus(StrEnum):
    """How far the calculation of a result can be relied upon.

    It is the ``calculation`` axis of
    :class:`~ccnl_engine.payroll.domain.assurance.ResultAssurance`; whether
    the amounts can be paid is the assurance payability, not this status.

    Members are listed from least to most severe.  Compare them with
    :attr:`severity` or combine them with :meth:`worst`; the string values
    do not sort in severity order.

    Attributes:
        FINAL: Every capability decided from known rules and facts.
        PROVISIONAL: Computed, but at least one decision rests on an
            assumption that may change the amounts once confirmed.
        INCOMPLETE: At least one amount could not be determined.
        REJECTED: The inputs cannot produce a meaningful result.
    """

    FINAL = "final"
    PROVISIONAL = "provisional"
    INCOMPLETE = "incomplete"
    REJECTED = "rejected"

    @property
    def severity(self) -> int:
        """Rank of this status, ``0`` for final up to ``3`` for rejected."""
        return _SEVERITY[self]

    @classmethod
    def worst(cls, statuses: Iterable[CalculationStatus]) -> CalculationStatus:
        """Return the most severe status in ``statuses``.

        Args:
            statuses: Statuses to combine, possibly empty.

        Returns:
            The status with the highest :attr:`severity`, or
            :attr:`FINAL` when ``statuses`` is empty.
        """
        return max(statuses, key=_SEVERITY.__getitem__, default=cls.FINAL)


class DecisionOrigin(StrEnum):
    """Where the rule behind a decision comes from.

    Attributes:
        ENGINE: The engine applied a rule of the bundled data or of the law.
        CALLER_SUPPLIED: The caller supplied a value (a rate, a multiplier,
            an amount) that stands in for a rule the engine would otherwise
            apply; no bundled source backs it.
    """

    ENGINE = "engine"
    CALLER_SUPPLIED = "caller_supplied"


_SEVERITY: dict[CalculationStatus, int] = {
    status: rank for rank, status in enumerate(CalculationStatus)
}


#: Public input field of each fact a missing-fact issue can name: the
#: field the caller sets to resolve the issue.
PUBLIC_FACTS: Mapping[str, str] = MappingProxyType({
    "activity": "EmployerProfile.activity",
    "agreement_signed_on": "BonusEvent.agreement_signed_on",
    "allocation_pct": "Dependent.allocation_pct",
    "category": "Employment.category",
    "cohabiting": "Dependent.cohabiting",
    "contribution_history": "Employment.contribution_history",
    "current_year": "PeriodInput.current_year",
    "employment_income": "PriorYearTaxFacts.employment_income",
    "full_time_weekly_hours": "Employment.full_time_weekly_hours",
    "naspi_exclusion": "FixedTerm.naspi_exclusion",
    "no_pay_due": "AbsenceEvent.no_pay_due",
    "opening_state": "PeriodInput.opening_state",
    "ordinary_hours_worked": "PeriodFacts.ordinary_hours_worked",
    "other_employers": "InpsBaseYtd.other_employers",
    "other_employers_additional_ivs": "InpsBaseYtd.other_employers_additional_ivs",
    "own_income": "Dependent.own_income",
    "pension_fund": "Employment.pension_fund",
    "renewals": "FixedTerm.renewals",
    "residency_eligibility": "Dependent.residency_eligibility",
    "reference_period": "ArrearsEvent.reference_period",
    "roles": "Employment.roles",
    "sector": "Employment.sector",
    "seniority": "Employment.seniority",
    "short_absence_exempt": "SicknessEpisode.short_absence_exempt",
    "sickness_known_from": "OpeningBalances.sickness_known_from",
    "suspends_accrual": "AbsenceEvent.suspends_accrual",
    "tfr_fund": "Employment.tfr_fund",
    "tfr_treasury_fund": "Employment.tfr_treasury_fund",
    "young_member": "PensionFundEnrolment.young_member",
    "erc_amount": "Employment.erc_amount",
})


def _require_code(value: str, name: str) -> None:
    if not _CODE_PATTERN.fullmatch(value):
        msg = f"{name} must be lower snake case (e.g. 'unknown_table'); got {value!r}"
        raise ValueError(msg)


def _require_text(value: str, name: str) -> None:
    if not value:
        msg = f"{name} must not be empty"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class CalculationIssue:
    """A condition that lowers the status of a calculation result.

    Attributes:
        code: Stable machine-readable identifier in lower snake case, e.g.
            ``"surtax_table_unknown"``.  Callers may branch on it.
        message: Human-readable explanation for the caller.
        status: Status the issue implies for the result that carries it.
        source: Normative source behind the issue, when one applies.
        fact: Name of the public input field whose absence raised the
            issue, e.g. ``"employment_income"``; one of
            :data:`PUBLIC_FACTS`, ``None`` when the issue is not about a
            missing fact.

    Raises:
        ValueError: When ``code`` is not lower snake case, ``fact`` is not
            one of :data:`PUBLIC_FACTS` or ``message`` is empty.
    """

    code: str
    message: str
    status: CalculationStatus
    source: SourceLocation | None = None
    fact: str | None = None

    def __post_init__(self) -> None:  # noqa: D105
        _require_code(self.code, "code")
        _require_text(self.message, "message")
        if self.fact is not None and self.fact not in PUBLIC_FACTS:
            msg = f"fact must be one of {sorted(PUBLIC_FACTS)}; got {self.fact!r}"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class CalculationDecision:
    """What one capability decided in a calculation, and why.

    Attributes:
        capability: Catalog feature name, e.g. ``"regional_surtax"``.
        status: Status implied by this decision.
        reason_code: Stable machine-readable reason in lower snake case,
            e.g. ``"table_found"``.
        rule: Identifier of the rule applied.
        rule_version: Version of the rule applied, e.g. the tax year or
            the data bundle version.
        inputs: Normalized inputs the decision was taken from.  Copied and
            read-only after construction.
        source: Normative source of the rule, when recorded.
        amount: Amount produced by the decision; ``None`` when the decision
            yields no amount or the amount is unknown.
        origin: Whether the engine applied the rule or the caller supplied
            it.  A caller-supplied decision cites no source.

    Raises:
        ValueError: When ``reason_code`` is not lower snake case, when
            ``capability``, ``rule`` or ``rule_version`` is empty, when
            ``amount`` is not finite, or when a caller-supplied decision
            cites a source.
    """

    capability: str
    status: CalculationStatus
    reason_code: str
    rule: str
    rule_version: str
    inputs: Mapping[str, Decimal | str] = field(default_factory=lambda: FrozenDict({}))
    source: SourceLocation | None = None
    amount: Decimal | None = None
    origin: DecisionOrigin = DecisionOrigin.ENGINE

    def __post_init__(self) -> None:  # noqa: D105
        _require_text(self.capability, "capability")
        _require_code(self.reason_code, "reason_code")
        _require_text(self.rule, "rule")
        _require_text(self.rule_version, "rule_version")
        if self.amount is not None and not self.amount.is_finite():
            msg = f"amount must be finite; got {self.amount}"
            raise ValueError(msg)
        if self.origin is DecisionOrigin.CALLER_SUPPLIED and self.source is not None:
            msg = "a caller-supplied decision cannot cite a source"
            raise ValueError(msg)
        object.__setattr__(self, "inputs", FrozenDict(dict(self.inputs)))
