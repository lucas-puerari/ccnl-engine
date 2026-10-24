"""The review log of a CCNL data file: reviews, sources and divergences."""

from __future__ import annotations

import datetime as dt
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReviewerKind(StrEnum):
    """Who made a review: a person or an AI model."""

    HUMAN = "human"
    AI = "ai"


class ReviewIndependence(StrEnum):
    """How far a review stands from the extraction of the values it checks.

    Values:
        same_process: The run that extracted the values also reviewed them;
            an interpretation error they share survives.
        separate_session: Another run of the same model, without the
            reasoning of the extraction, re-read the source.
        separate_model: A different model re-read the source.
        human: A person re-read the source.
    """

    SAME_PROCESS = "same_process"
    SEPARATE_SESSION = "separate_session"
    SEPARATE_MODEL = "separate_model"
    HUMAN = "human"


class ReviewOutcome(StrEnum):
    """What a review did to the ruleset.

    Values:
        confirmed: The checked values match their sources.
        corrected: The review fixed values that did not match.
        flagged: The review left values to correct or to re-check.
        demoted: The review lowered the readiness of the ruleset.
    """

    CONFIRMED = "confirmed"
    CORRECTED = "corrected"
    FLAGGED = "flagged"
    DEMOTED = "demoted"


class DivergenceDecision(StrEnum):
    """How a difference from an independent output was closed.

    Values:
        engine_bug: The engine was wrong; it was fixed and a regression
            test pins the independent value.
        source_context_missing: The output omits a fact the comparison
            needs; a limitation of the file blocks the runs concerned.
        accepted_external_variance: The difference is explained and kept,
            until a date by which it is looked at again.
        external_artifact_error: The output is incoherent for the case
            compared (another year, another scope); it is no evidence.
    """

    ENGINE_BUG = "engine_bug"
    SOURCE_CONTEXT_MISSING = "source_context_missing"
    ACCEPTED_EXTERNAL_VARIANCE = "accepted_external_variance"
    EXTERNAL_ARTIFACT_ERROR = "external_artifact_error"


class Divergence(BaseModel):
    """A difference a review found against an independent output, closed.

    A difference never stays open: it is closed by one decision, and the
    decision names what makes it testable.  Who answers for it is the owner
    of the ruleset (``verification.owner``).

    Attributes:
        subject: What differs, with both values.
        decision: How the difference was closed.
        cause: Why the values differ, as far as it is known.
        evidence: Where the decision is enforced: the regression test of
            an ``engine_bug``, or the document read.
        limitation: For ``source_context_missing``, the variant of the
            limitation of the file that blocks the runs concerned.
        review_by: For ``accepted_external_variance``, the date by which
            the variance is looked at again.

    Raises:
        ValueError: When the decision lacks the field it requires.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    subject: str = Field(min_length=1)
    decision: DivergenceDecision
    cause: str = Field(min_length=1)
    evidence: str = Field(min_length=1)
    limitation: str | None = None
    review_by: dt.date | None = None

    @model_validator(mode="after")
    def _decision_is_testable(self) -> Self:
        context = self.decision is DivergenceDecision.SOURCE_CONTEXT_MISSING
        if context != (self.limitation is not None):
            msg = "exactly a source_context_missing divergence names its limitation"
            raise ValueError(msg)
        variance = self.decision is DivergenceDecision.ACCEPTED_EXTERNAL_VARIANCE
        if variance != (self.review_by is not None):
            msg = "exactly an accepted_external_variance divergence has a review_by"
            raise ValueError(msg)
        return self


class ReviewSource(BaseModel):
    """A document a review read, pinned by its hash.

    Attributes:
        url: Where the document was fetched.
        sha256: Digest of the fetched document, so a later review can tell
            whether it changed.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str
    sha256: str


class CCNLReview(BaseModel):
    """One entry of the review log of a CCNL data file.

    The same fields record a review by a person and by an AI model. A rule
    the review checked points to it with ``extraction.review_id``.

    Attributes:
        id: Identifier of the entry, unique in the file.
        date: Day the review was made.
        reviewer: Role of the person (``maintainer``), or identifier of
            the model.
        reviewer_kind: Whether the reviewer is a person or an AI model.
        scope: What the review checked: the whole file, or which rules.
        independence: How far the review stands from the extraction of
            the values it checks; ``None`` on entries written before the
            field existed (24 October 2026).
        checked: The fields or values the review compared with its
            sources, e.g. ``levels[C3].base_salary 2026-06-01``.
        outcome: What the review did to the ruleset.
        sources: Documents the review read; empty when none was recorded.
        findings: Differences the review found, or notes on its scope.
        divergences: Differences from an independent output, each closed
            by a decision.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    date: dt.date
    reviewer: str
    reviewer_kind: ReviewerKind
    scope: str
    independence: ReviewIndependence | None = None
    checked: tuple[str, ...] = ()
    outcome: ReviewOutcome
    sources: tuple[ReviewSource, ...] = ()
    findings: tuple[str, ...] = ()
    divergences: tuple[Divergence, ...] = ()
