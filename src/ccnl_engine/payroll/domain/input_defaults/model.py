"""Classification of a default of a public input field.

A field of a public input type that has a default is one of two kinds:

- ``absence_is_fact``: leaving the field to its default states the fact
  (no event happened, the employment has not ended, the worker did not
  waive a regime); the default never selects a branch the caller did not
  mean;
- ``requires_fact``: the default stands for a fact the caller has not
  stated, so a capability must not treat it as that fact.  How the run
  honours it is the :class:`FactEnforcement`: a requirement of the
  capability registry, a fact the run reports as missing, or still pending,
  when the default selects a branch without a blocker.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = [
    "DefaultPolicy",
    "FactEnforcement",
    "FieldDefault",
    "absence_is_fact",
    "requires_fact",
]


class DefaultPolicy(StrEnum):
    """What the default of a public input field means.

    Attributes:
        ABSENCE_IS_FACT: The default is the fact itself.
        REQUIRES_FACT: The default stands for a fact the caller has not
            stated.
    """

    ABSENCE_IS_FACT = "absence_is_fact"
    REQUIRES_FACT = "requires_fact"


class FactEnforcement(StrEnum):
    """How a run honours a ``requires_fact`` field left to its default.

    Attributes:
        REQUIREMENT: The fact is an applicability fact of the capability
            registry: a run that does not rule the capability out has a
            ``requirement_unresolved`` blocker.
        REPORTED: The run raises a ``missing_fact`` issue or an input
            error naming the fact when the capability needs it.
        PENDING: Not honoured yet: the default selects a branch of the
            capability without a blocker.
    """

    REQUIREMENT = "requirement"
    REPORTED = "reported"
    PENDING = "pending"


@dataclass(frozen=True, slots=True)
class FieldDefault:
    """Classification of the default of one public input field.

    Attributes:
        policy: What the default means.
        reason: Why, for a human reader: what the default stands for.
        capability: For ``requires_fact``, the capability the fact feeds.
        fact: For ``requires_fact``, the path of the fact, in the notation
            of the capability registry (e.g. ``"facts.regione"``).
        enforcement: For ``requires_fact``, how a run honours it.

    Raises:
        ValueError: When the capability, fact and enforcement are not all
            set for ``requires_fact`` and all unset for ``absence_is_fact``.
    """

    policy: DefaultPolicy
    reason: str
    capability: str | None = None
    fact: str | None = None
    enforcement: FactEnforcement | None = None

    def __post_init__(self) -> None:  # noqa: D105
        targets = (self.capability, self.fact, self.enforcement)
        set_targets = sum(t is not None for t in targets)
        expected = 3 if self.policy is DefaultPolicy.REQUIRES_FACT else 0
        if not self.reason or set_targets != expected:
            msg = (
                f"{self.policy} default: a reason is required, and capability, "
                f"fact and enforcement are set exactly for requires_fact; got "
                f"{targets}"
            )
            raise ValueError(msg)


def absence_is_fact(reason: str) -> FieldDefault:
    """Return the classification of a default that states the fact.

    Returns:
        An ``absence_is_fact`` classification.
    """
    return FieldDefault(DefaultPolicy.ABSENCE_IS_FACT, reason)


def requires_fact(
    capability: str, fact: str, enforcement: FactEnforcement, reason: str
) -> FieldDefault:
    """Return the classification of a default that stands for an unstated fact.

    Returns:
        A ``requires_fact`` classification.
    """
    return FieldDefault(
        DefaultPolicy.REQUIRES_FACT, reason, capability, fact, enforcement
    )
