"""Census of a CCNL: one requirement record per economic institute and variant.

The census lists what a CCNL text owes, institute by institute and variant
by variant, and where the engine stands on each: the source clause, the
fact that selects the rule, where its data and formula live, the code that
computes it, the state of the rule and the scenarios that verify it.  It is
the checklist the completeness report reads; a CCNL without a census is
incomplete, never complete by default.

A row never stores whether its work is open: the report derives it from the
state, the scenarios and the limitation or weak rule the row links, so the
census cannot disagree with the limitations it tracks.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "Census",
    "CensusOrigin",
    "Requirement",
    "RequirementLinks",
    "RequirementSource",
    "RuleState",
]

#: Lower snake case identifier, the format of limitation variants.
_SNAKE = r"^[a-z][a-z0-9_]*$"
#: A work item of the completion plan: ``T03.05`` or ``G13.02``.
WORK_ITEM = re.compile(r"[TG]\d\d\.\d\d")


class RuleState(StrEnum):
    """Where the engine stands on the rule of a requirement.

    Attributes:
        IMPLEMENTED: The engine resolves the rule from the bundle and the
            facts of the run.
        ZERO: The contract sets the amount to zero, a rule of its own (a
            verified treatment without integration).
        NOT_APPLICABLE: The contract excludes the institute for the
            variant; the source states where.
        ABSENT: The rule applies and the engine does not compute it.
        UNVERIFIED: The engine computes it, the reading is not confirmed.
    """

    IMPLEMENTED = "implemented"
    ZERO = "zero"
    NOT_APPLICABLE = "not_applicable"
    ABSENT = "absent"
    UNVERIFIED = "unverified"


class CensusOrigin(StrEnum):
    """How a requirement entered the census.

    Attributes:
        TEXT: Read from the contract text, article by article.
        SEEDED: Carried over from a limitation, a note or a weak rule of
            the bundle, pending the reading of the text.
    """

    TEXT = "text"
    SEEDED = "seeded"


class RequirementSource(BaseModel):
    """The clause a requirement comes from.

    Attributes:
        document_id: A ``meta.sources`` document of the CCNL.
        section: Article, paragraph or table of the document.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: str = Field(min_length=1)
    section: str = Field(min_length=1)


class RequirementLinks(BaseModel):
    """The bundle objects a requirement tracks, its open work derived from them.

    Attributes:
        limitations: Ids of the limitations whose closing closes the row.
        rules: Paths of payable rules, ``<file>#<path>`` as the provenance
            inventory names them, whose weak status keeps the row open.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    limitations: tuple[str, ...] = ()
    rules: tuple[str, ...] = ()


class Requirement(BaseModel):
    """One economic institute of a CCNL for one variant.

    Attributes:
        id: Lower snake case, unique within the census.
        institute: The institute (e.g. ``sickness``), a registry capability
            name when the engine has one.
        variant: The variant it covers: level group, category, profile,
            cohort, relationship, hours, regime, territory or period;
            ``all`` when the institute does not vary.
        source: Clause of the text; required unless the row is seeded.
        discriminant: The fact of the run that selects the rule.
        rule: Where the data and the formula live in the bundle.
        calculation: The code or capability that computes it.
        state: Where the engine stands.
        scenarios: Test node ids or reference case ids that verify the row.
        work: Work items of the completion plan that close it.
        verification: Work items whose check verifies the row once its
            work is done (``T03.11`` for a sickness row); required while
            the row is open, as its ``work``.
        origin: How the row entered the census.
        links: Limitations and weak rules whose state the row follows.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(pattern=_SNAKE, max_length=64)
    institute: str = Field(pattern=_SNAKE)
    variant: str = Field(pattern=_SNAKE)
    source: RequirementSource | None = None
    discriminant: str = ""
    rule: str = ""
    calculation: str = ""
    state: RuleState
    scenarios: tuple[str, ...] = ()
    work: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    origin: CensusOrigin = CensusOrigin.TEXT
    links: RequirementLinks = RequirementLinks()

    @property
    def open(self) -> bool:
        """Whether the row is open by itself: seeded, or its rule is open."""
        return self.origin is CensusOrigin.SEEDED or self.state in {
            RuleState.ABSENT,
            RuleState.UNVERIFIED,
        }

    @model_validator(mode="after")
    def _check_items(self) -> Self:
        wrong = [
            item
            for item in (*self.work, *self.verification)
            if not WORK_ITEM.fullmatch(item)
        ]
        if wrong:
            msg = f"requirement {self.id}: work items {wrong} are not T00.00/G00.00"
            raise ValueError(msg)
        if self.open and not (self.work and self.verification):
            msg = (
                f"requirement {self.id}: an open row names its work item and "
                "its planned verification"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.origin is CensusOrigin.TEXT and self.source is None:
            msg = f"requirement {self.id}: a row read from the text names its source"
            raise ValueError(msg)
        if self.state is RuleState.NOT_APPLICABLE and self.source is None:
            msg = f"requirement {self.id}: non-applicability needs a source"
            raise ValueError(msg)
        return self


class Census(BaseModel):
    """The requirement records of one CCNL.

    Attributes:
        schema_version: Version of the census format.
        ccnl_id: The CCNL the census covers.
        requirements: The rows, sorted by id.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int
    ccnl_id: str = Field(min_length=1)
    requirements: tuple[Requirement, ...] = ()

    @model_validator(mode="after")
    def _check_ids(self) -> Self:
        ids = [row.id for row in self.requirements]
        if ids != sorted(set(ids)):
            msg = f"census {self.ccnl_id}: requirement ids must be sorted and unique"
            raise ValueError(msg)
        return self
