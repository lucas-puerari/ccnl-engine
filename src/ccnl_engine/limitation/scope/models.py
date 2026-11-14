"""The scope of a limitation: the runs it concerns, and the facts of a run.

A :class:`LimitationScope` narrows a limitation to some contract types,
levels, categories, run kinds, seniority, headcount and dates;
:class:`LimitationFacts` are the facts of one run it is matched against.
An unknown fact never rules a run out.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = ["LimitationFacts", "LimitationScope", "LimitationTrigger"]


class LimitationTrigger(StrEnum):
    """What makes a limitation concern a run.

    Attributes:
        RUN: A run of an affected ruleset whose facts match the scope.
        PATH: A run that traverses the code path of the limitation; the
            engine reports the traversal.
        OWED: An amount the contract owes in every run of an affected
            ruleset that the scope matches, which the engine does not
            compute: it concerns the run whether or not its capability
            applies (a health fund paid for every worker).
        OUTSIDE_INPUT: The fact that triggers it has no field in the
            request, so no run can be told apart: it is documented only.
            It is never an amount owed in every run (that one is ``owed``).
    """

    RUN = "run"
    PATH = "path"
    OWED = "owed"
    OUTSIDE_INPUT = "outside_input"


ContractTypeName = Literal["permanent", "fixed_term", "apprentice"]
WorkerCategoryName = Literal["operaio", "impiegato", "quadro", "dirigente"]
RunKindName = Literal[
    "regular", "thirteenth", "fourteenth", "adjustment", "termination"
]


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
        headcount: Employer headcount, ``None`` when unknown.
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
    headcount: int | None = None


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
        headcount_from: Least employer headcount concerned (a rate that
            changes above a size threshold).
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
    headcount_from: int | None = Field(None, ge=2)
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
            and _at_least(self.seniority_months_from, facts.seniority_months)
            and _at_least(self.headcount_from, facts.headcount)
            and (self.effective_from is None or facts.as_of >= self.effective_from)
            and (self.effective_until is None or facts.as_of < self.effective_until)
        )


def _within(allowed: frozenset[str] | None, value: str) -> bool:
    return allowed is None or value in allowed


def _at_least(threshold: int | None, value: int | None) -> bool:
    """Return whether a known fact reaches the threshold.

    Returns:
        ``True`` without a threshold, for an unknown fact, or at or above it.
    """
    return threshold is None or value is None or value >= threshold
