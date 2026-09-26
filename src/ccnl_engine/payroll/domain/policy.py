"""Data-driven policy resolver for the period-first payroll engine.

:class:`PolicyResolver` maps pay-item kinds to per-axis treatment outcomes
from an ordered list of rules. Loading the bundled ruleset is a service
concern: see :func:`~ccnl_engine.payroll.service.policy_loader.load_policy_resolver`.

Each axis independently reports one of its concrete treatment values,
``NOT_APPLICABLE`` (the concept does not apply to this item type), or
``UNKNOWN`` (the outcome depends on context not yet available).  Call
:func:`require` to assert that a given axis is resolved before relying on it.

Design notes:
- Rules are ordered; the first match (kind + date range) wins.
- ``NOT_APPLICABLE`` is distinct from ``EXCLUDED``: the latter means the item
  enters the base but at zero; the former means the axis is irrelevant.
- ``UNKNOWN`` should block computation at the call site via :func:`require`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Literal

__all__ = [
    "ContributionAxis",
    "CostAxis",
    "PolicyContext",
    "PolicyResolution",
    "PolicyResolver",
    "TaxAxis",
    "TfrAxis",
    "UnresolvablePolicyError",
    "require",
]


class TaxAxis(StrEnum):
    """IRPEF treatment for this item, or a resolver meta-status."""

    ORDINARY = "ordinary"
    SEPARATE = "separate"
    SUBSTITUTE = "substitute"
    EXEMPT = "exempt"
    NON_CASH_TAXABLE = "non_cash_taxable"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class ContributionAxis(StrEnum):
    """INPS contribution base treatment, or a resolver meta-status."""

    INCLUDED = "included"
    EXCLUDED = "excluded"
    CAPPED = "capped"
    SPECIAL_BASE = "special_base"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class TfrAxis(StrEnum):
    """TFR accrual base treatment, or a resolver meta-status."""

    INCLUDED = "included"
    EXCLUDED = "excluded"
    SPECIAL = "special"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class CostAxis(StrEnum):
    """Employer-cost perspective treatment, or a resolver meta-status."""

    EMPLOYEE_CASH = "employee_cash"
    EMPLOYER_COST = "employer_cost"
    THIRD_PARTY_CASH = "third_party_cash"
    ACCRUAL_ONLY = "accrual_only"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PolicyContext:
    """Contextual facts supplied by the caller to narrow rule selection.

    Attributes:
        year: Tax year of the payroll calculation.
        as_of: Reference date for rule effective-range matching.
        ccnl_slug: Identifies the applicable CCNL, or ``None`` if unknown.
        sector: Tax sector code, or ``None`` if not yet determined.
        gross_ytd: Year-to-date gross earnings for threshold checks.
        is_manager: Whether the worker is a dirigente.
    """

    year: int
    as_of: date
    ccnl_slug: str | None = None
    sector: str | None = None
    gross_ytd: Decimal = Decimal(0)
    is_manager: bool = False


@dataclass(frozen=True)
class PolicyResolution:
    """Per-axis resolution for one pay-item kind.

    Attributes:
        policy_id: Stable identifier for the matched rule.
        policy_version: Version tag of the ruleset that produced this result.
        effective_from: Start of the rule's effective date range.
        effective_until: End of the range, or ``None`` for open-ended rules.
        tax: IRPEF treatment outcome.
        contribution: INPS contribution base outcome.
        tfr: TFR accrual base outcome.
        cost: Employer cost perspective outcome.
        legal_basis: Normative reference for the rule.
    """

    policy_id: str
    policy_version: str
    effective_from: date
    effective_until: date | None
    tax: TaxAxis
    contribution: ContributionAxis
    tfr: TfrAxis
    cost: CostAxis
    legal_basis: str


_Axis = Literal["tax", "contribution", "tfr", "cost"]


class UnresolvablePolicyError(Exception):
    """Raised when a determinant axis carries ``UNKNOWN`` on a resolution.

    Attributes:
        policy_id: The policy rule that produced the UNKNOWN outcome.
        axis: The axis that is UNKNOWN (``"tax"``, ``"contribution"``, etc.).
        resolution: The full resolution for inspection or logging.
    """

    def __init__(
        self,
        policy_id: str,
        axis: str,
        resolution: PolicyResolution,
    ) -> None:
        """Store axis, policy_id, and full resolution for caller inspection."""
        super().__init__(f"Policy axis '{axis}' is UNKNOWN for policy '{policy_id}'")
        self.policy_id = policy_id
        self.axis = axis
        self.resolution = resolution


def require(resolution: PolicyResolution, axis: _Axis) -> PolicyResolution:
    """Assert that *axis* is not ``UNKNOWN`` on *resolution*.

    Args:
        resolution: The resolution to check.
        axis: One of ``"tax"``, ``"contribution"``, ``"tfr"``, ``"cost"``.

    Returns:
        *resolution* unchanged when the axis is not ``UNKNOWN``.

    Raises:
        UnresolvablePolicyError: When the axis value is ``UNKNOWN``.
    """
    val = getattr(resolution, axis)
    if str(val) == "unknown":
        raise UnresolvablePolicyError(resolution.policy_id, axis, resolution)
    return resolution


@dataclass(frozen=True)
class _Rule:
    """Internal representation of one parsed JSON policy rule."""

    policy_id: str
    policy_version: str
    kinds: tuple[str, ...]
    effective_from: date
    effective_until: date | None
    tax: str
    contribution: str
    tfr: str
    cost: str
    legal_basis: str

    @classmethod
    def from_dict(cls, d: dict[str, object]) -> _Rule:
        """Parse a rule from a raw JSON dict.

        Returns:
            A :class:`_Rule` instance with typed fields.
        """
        until_raw = d["effective_until"]
        effective_until = (
            date.fromisoformat(str(until_raw)) if until_raw is not None else None
        )
        return cls(
            policy_id=str(d["policy_id"]),
            policy_version=str(d["policy_version"]),
            kinds=tuple(str(k) for k in d["kinds"]),  # type: ignore[attr-defined]
            effective_from=date.fromisoformat(str(d["effective_from"])),
            effective_until=effective_until,
            tax=str(d["tax"]),
            contribution=str(d["contribution"]),
            tfr=str(d["tfr"]),
            cost=str(d["cost"]),
            legal_basis=str(d["legal_basis"]),
        )


class PolicyResolver:
    """Data-driven resolver backed by the bundled Italian policy ruleset.

    Rules are indexed by pay-item kind.  :meth:`resolve` walks the list for
    the matched kind in order and returns the first rule whose effective date
    range contains ``context.as_of``.
    """

    def __init__(self, rules: list[_Rule]) -> None:
        """Index *rules* by pay-item kind for O(1) kind lookup."""
        self._index: dict[str, list[_Rule]] = {}
        for rule in rules:
            for kind in rule.kinds:
                self._index.setdefault(kind, []).append(rule)

    def resolve(
        self,
        kind: str,
        context: PolicyContext,
    ) -> PolicyResolution | None:
        """Return the first rule matching *kind* and *context.as_of*, or None.

        Args:
            kind: Pay-item kind string (e.g. ``"base_salary_earning"``).
            context: Resolver context providing the reference date and facts.

        Returns:
            A :class:`PolicyResolution`, or ``None`` when no rule covers
            *kind* on ``context.as_of``.
        """
        rules = self._index.get(kind)
        if rules is None:
            return None
        for rule in rules:
            if context.as_of < rule.effective_from:
                continue
            if (
                rule.effective_until is not None
                and context.as_of > rule.effective_until
            ):
                continue
            return PolicyResolution(
                policy_id=rule.policy_id,
                policy_version=rule.policy_version,
                effective_from=rule.effective_from,
                effective_until=rule.effective_until,
                tax=TaxAxis(rule.tax),
                contribution=ContributionAxis(rule.contribution),
                tfr=TfrAxis(rule.tfr),
                cost=CostAxis(rule.cost),
                legal_basis=rule.legal_basis,
            )
        return None
