"""Model limitations: known simplifications as typed, executable data.

A :class:`ModelLimitation` is a place where the engine knowingly computes
something other than what the contract says, or cannot tell whether it
does.  Each one names the capability and variant it limits, the rulesets
and dates it affects, whether it can move an amount
(:class:`MonetaryImpact`), whether it is still :attr:`~LimitationStatus.OPEN`
and what closes it.

Limitations come from two places, both in the knowledge bundle:

- the ``simplification`` notes of a CCNL file, which carry an inline
  limitation (``ccnl_engine.agreement.facade.CoverageNote``);
- the engine limitations of code paths shared by several CCNLs
  (``knowledge/limitation/engine.json``), recorded when the run
  traverses the path.

:meth:`ModelLimitation.applies_to` decides from :class:`LimitationFacts`
whether a limitation concerns a run; an applicable limitation that
:attr:`~ModelLimitation.blocks` makes the totals it names
(:attr:`~ModelLimitation.totals`) unreliable, so the result is not payable.

The trigger classifies a limitation by obligation: an amount the contract
owes in every run it scopes is ``owed`` and always concerns those runs; an
amount owed only on a fact the request has no field for is
``outside_input`` and is documented without concerning any run.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.limitation.scope.models import (
    LimitationFacts,
    LimitationScope,
    LimitationTrigger,
)
from ccnl_engine.limitation.types import ALL_TOTALS, ResultTotal

__all__ = [
    "HOLDING",
    "LimitationFacts",
    "LimitationScope",
    "LimitationStatus",
    "ModelLimitation",
    "MonetaryImpact",
    "NoteLimitation",
    "SearchedDocument",
]

#: Lower snake case identifier of a variant.
_VARIANT = r"^[a-z][a-z0-9_]*$"


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
        UNSOURCED: A declared residual: a documented search of the law,
            the INPS and Ministry practice and the signed text found no
            source and no statutory default for the case. The engine still
            computes the simplified amount, so it keeps blocking the runs
            it concerns; it is listed apart from the open work.
    """

    OPEN = "open"
    RESOLVED = "resolved"
    UNSOURCED = "unsourced"


#: Statuses of a limitation that still holds.
HOLDING = frozenset({LimitationStatus.OPEN, LimitationStatus.UNSOURCED})


class SearchedDocument(BaseModel):
    """A document read without finding the source of a declared residual.

    Attributes:
        url: Where the document was downloaded from.
        sha256: Lowercase hex sha256 of the file read.
        title: What the document is, for a human reader.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str = Field(pattern=r"^https?://")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    title: str = Field(min_length=1)


def _require_search(
    status: LimitationStatus, searched: tuple[SearchedDocument, ...], name: str
) -> None:
    """Require the search evidence on a declared residual, and only there.

    Raises:
        ValueError: When an unsourced limitation lists no document read, or
            another status lists some.
    """
    unsourced = status is LimitationStatus.UNSOURCED
    if unsourced and not searched:
        msg = f"limitation {name}: an unsourced limitation lists the documents searched"
        raise ValueError(msg)
    if searched and not unsourced:
        msg = (
            f"limitation {name}: only an unsourced limitation lists documents searched"
        )
        raise ValueError(msg)


class NoteLimitation(BaseModel):
    """The limitation a ``simplification`` note of a CCNL file declares.

    Its id is ``<ccnl id>/<variant>``; its capability, impact and summary
    are those of the note.

    Attributes:
        variant: Lower snake case name, unique within the CCNL.
        applies_when: The runs of the CCNL it concerns.
        totals: The totals of a run it can make wrong.
        status: Whether it still holds.
        remediation: What closes it, for a human reader.
        searched: The documents read, for an unsourced limitation only.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    variant: str = Field(pattern=_VARIANT, max_length=48)
    applies_when: LimitationScope = LimitationScope()
    totals: frozenset[ResultTotal] = Field(ALL_TOTALS, min_length=1)
    status: LimitationStatus = LimitationStatus.OPEN
    remediation: str = Field(min_length=1)
    searched: tuple[SearchedDocument, ...] = ()

    @model_validator(mode="after")
    def _check_searched(self) -> Self:
        _require_search(self.status, self.searched, self.variant)
        return self


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
        totals: The totals of a run it can make wrong: both by default,
            the employer cost alone for an amount only the employer pays.
        source: Where it is declared: the CCNL file or the engine module.
        remediation: What closes it.
        searched: The documents read, for an unsourced limitation only.
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
    totals: frozenset[ResultTotal] = Field(ALL_TOTALS, min_length=1)
    source: str = Field(min_length=1)
    remediation: str = Field(min_length=1)
    searched: tuple[SearchedDocument, ...] = ()

    @model_validator(mode="after")
    def _check_searched(self) -> Self:
        _require_search(self.status, self.searched, self.id)
        return self

    @property
    def blocks(self) -> bool:
        """Whether it makes a result it applies to not payable.

        Returns:
            ``True`` for an open or unsourced limitation whose monetary
            impact is ``yes`` or ``unknown``: a declared residual still
            computes the simplified amount.
        """
        return self.status in HOLDING and self.monetary_impact is not MonetaryImpact.NO

    def applies_to(self, facts: LimitationFacts) -> bool:
        """Return whether the limitation concerns the run of *facts*.

        An ``owed`` limitation concerns every run of an affected CCNL.
        Otherwise the capability must concern the run: a ``path``
        limitation concerns it when the run traversed its path, whatever
        the CCNL; a ``run`` limitation when the CCNL is affected; an
        ``outside_input`` one never.  The scope must match in every case.

        Returns:
            ``True`` when the limitation concerns the run.
        """
        trigger = self.applies_when.trigger
        if trigger is LimitationTrigger.OUTSIDE_INPUT:
            return False
        if trigger is LimitationTrigger.OWED:
            return facts.ccnl_id in self.rulesets and self.applies_when.matches(facts)
        if self.capability not in facts.applicable:
            return False
        concerned = (
            self.id in facts.traversed
            if trigger is LimitationTrigger.PATH
            else facts.ccnl_id in self.rulesets
        )
        return concerned and self.applies_when.matches(facts)
