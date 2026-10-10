"""Model limitations: known simplifications as typed, executable data.

A :class:`ModelLimitation` is a place where the engine knowingly computes
something other than what the contract says, or cannot tell whether it
does.  Each one names the capability and variant it limits, the rulesets
and dates it affects, whether it can move an amount
(:class:`MonetaryImpact`), whether it is still :attr:`~LimitationStatus.OPEN`
and what closes it.

Limitations come from two places, both in the knowledge bundle:

- the ``simplification`` notes of a CCNL file, which carry an inline
  limitation (``ccnl_engine.contract.identity.facade.CoverageNote``);
- the engine limitations of code paths shared by several CCNLs
  (``knowledge/limitation/engine.json``), recorded when the run
  traverses the path.

:meth:`ModelLimitation.applies_to` decides from :class:`LimitationFacts`
whether a limitation concerns a run; an applicable limitation that
:attr:`~ModelLimitation.blocks` makes the result not payable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003 - pydantic resolves the annotation
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "LimitationFacts",
    "LimitationScope",
    "LimitationStatus",
    "LimitationTrigger",
    "ModelLimitation",
    "MonetaryImpact",
    "NoteLimitation",
]

#: Lower snake case identifier of a variant.
_VARIANT = r"^[a-z][a-z0-9_]*$"

ContractTypeName = Literal["permanent", "fixed_term", "apprentice"]
WorkerCategoryName = Literal["operaio", "impiegato", "quadro", "dirigente"]
RunKindName = Literal[
    "regular", "thirteenth", "fourteenth", "adjustment", "termination"
]


class MonetaryImpact(StrEnum):
    """Whether a limitation can change an amount the engine computes.

    Attributes:
        YES: In the cases it applies to, an amount is known to differ from
            the contract.
        NO: No amount the engine computes from the bundle changes: the
            engine refuses the case, or reads the value from the caller.
        UNKNOWN: An amount may differ; the contract reading or the source
            is not confirmed.
    """

    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class LimitationStatus(StrEnum):
    """Whether a limitation still holds.

    Attributes:
        OPEN: The engine still computes the simplified amount.
        RESOLVED: The model was corrected, with a source and a test.
    """

    OPEN = "open"
    RESOLVED = "resolved"


class LimitationTrigger(StrEnum):
    """What makes a limitation concern a run.

    Attributes:
        RUN: A run of an affected ruleset whose facts match the scope.
        PATH: A run that traverses the code path of the limitation; the
            engine reports the traversal.
        OUTSIDE_INPUT: The fact that triggers it has no field in the
            request, so no run can be told apart: it is documented only.
    """

    RUN = "run"
    PATH = "path"
    OUTSIDE_INPUT = "outside_input"


@dataclass(frozen=True)
class LimitationFacts:
    """Facts of one run that the scope of a limitation is matched against.

    Attributes:
        ccnl_id: Identifier of the CCNL of the run.
        as_of: Date the rules of the run were read at.
        contract_type: ``permanent``, ``fixed_term`` or ``apprentice``.
        level_code: Classification level of the request.
        worker_category: Category of the worker, ``None`` when unknown.
        run_kind: Kind of the run (``regular``, ``thirteenth``...).
        seniority_months: Seniority of the worker, ``None`` when unknown.
        applicable: Capabilities that concern the run.
        traversed: Ids of the engine limitations whose path the run took.
    """

    ccnl_id: str
    as_of: date
    contract_type: str
    level_code: str
    worker_category: str | None
    run_kind: str
    seniority_months: int | None
    applicable: frozenset[str]
    traversed: frozenset[str] = frozenset()


class LimitationScope(BaseModel):
    """The runs a limitation concerns: every restriction set must match.

    A restriction left ``None`` does not narrow the scope.  An unknown fact
    (worker category, seniority) never rules a run out: what cannot be told
    apart is kept.

    Attributes:
        trigger: What makes the limitation concern a run.
        contract_types: Contract types concerned.
        levels: Level codes concerned.
        worker_categories: Worker categories concerned.
        run_kinds: Run kinds concerned (an allowance paid fewer times a
            year only matters in an extra-month run).
        seniority_months_from: Least seniority, in months, concerned.
        effective_from: First date concerned.
        effective_until: First date no longer concerned.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    trigger: LimitationTrigger = LimitationTrigger.RUN
    contract_types: frozenset[ContractTypeName] | None = Field(None, min_length=1)
    levels: frozenset[str] | None = Field(None, min_length=1)
    worker_categories: frozenset[WorkerCategoryName] | None = Field(None, min_length=1)
    run_kinds: frozenset[RunKindName] | None = Field(None, min_length=1)
    seniority_months_from: int | None = Field(None, ge=1)
    effective_from: date | None = None
    effective_until: date | None = None

    @model_validator(mode="after")
    def _ordered_dates(self) -> Self:
        start, end = self.effective_from, self.effective_until
        if start is not None and end is not None and end <= start:
            msg = f"effective_until {end} must follow effective_from {start}"
            raise ValueError(msg)
        return self

    def matches(self, facts: LimitationFacts) -> bool:
        """Return whether the facts of a run fall within the scope.

        Returns:
            ``True`` when every restriction set matches the facts.
        """
        return (
            _within(self.contract_types, facts.contract_type)
            and _within(self.levels, facts.level_code)
            and _within(self.run_kinds, facts.run_kind)
            and (
                facts.worker_category is None
                or _within(self.worker_categories, facts.worker_category)
            )
            and (
                self.seniority_months_from is None
                or facts.seniority_months is None
                or facts.seniority_months >= self.seniority_months_from
            )
            and (self.effective_from is None or facts.as_of >= self.effective_from)
            and (self.effective_until is None or facts.as_of < self.effective_until)
        )


def _within(allowed: frozenset[str] | None, value: str) -> bool:
    return allowed is None or value in allowed


class NoteLimitation(BaseModel):
    """The limitation a ``simplification`` note of a CCNL file declares.

    Its id is ``<ccnl id>/<variant>``; its capability, impact and summary
    are those of the note.

    Attributes:
        variant: Lower snake case name, unique within the CCNL.
        applies_when: The runs of the CCNL it concerns.
        status: Whether it still holds.
        remediation: What closes it, for a human reader.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    variant: str = Field(pattern=_VARIANT, max_length=48)
    applies_when: LimitationScope = LimitationScope()
    status: LimitationStatus = LimitationStatus.OPEN
    remediation: str = Field(min_length=1)


class ModelLimitation(BaseModel):
    """A known simplification of the engine, typed and executable.

    Attributes:
        id: Stable identifier: ``<ccnl id>/<variant>`` for a CCNL note,
            the bare variant name for an engine limitation.
        capability: Registry capability the limitation concerns.
        variant: Variant of the capability it concerns.
        summary: What the engine does differently, for a human reader.
        monetary_impact: Whether it can change an amount.
        status: Whether it still holds.
        rulesets: Ids of the CCNLs it affects.
        applies_when: The runs it concerns.
        source: Where it is declared: the CCNL file or the engine module.
        remediation: What closes it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    variant: str = Field(pattern=_VARIANT)
    summary: str = Field(min_length=1)
    monetary_impact: MonetaryImpact
    status: LimitationStatus = LimitationStatus.OPEN
    rulesets: tuple[str, ...] = Field(min_length=1)
    applies_when: LimitationScope = LimitationScope()
    source: str = Field(min_length=1)
    remediation: str = Field(min_length=1)

    @property
    def blocks(self) -> bool:
        """Whether it makes a result it applies to not payable.

        Returns:
            ``True`` for an open limitation whose monetary impact is
            ``yes`` or ``unknown``.
        """
        return (
            self.status is LimitationStatus.OPEN
            and self.monetary_impact is not MonetaryImpact.NO
        )

    def applies_to(self, facts: LimitationFacts) -> bool:
        """Return whether the limitation concerns the run of *facts*.

        The capability must concern the run.  A ``path`` limitation
        concerns it when the run traversed its path, whatever the CCNL; a
        ``run`` limitation when the CCNL is affected; an ``outside_input``
        one never.  The scope must match in every case.

        Returns:
            ``True`` when the limitation concerns the run.
        """
        trigger = self.applies_when.trigger
        if trigger is LimitationTrigger.OUTSIDE_INPUT:
            return False
        if self.capability not in facts.applicable:
            return False
        concerned = (
            self.id in facts.traversed
            if trigger is LimitationTrigger.PATH
            else facts.ccnl_id in self.rulesets
        )
        return concerned and self.applies_when.matches(facts)
