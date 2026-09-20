"""Coverage metadata: Coverage dataclass for payroll result quality information."""

from __future__ import annotations

import dataclasses
import typing
from dataclasses import dataclass, field
from typing import Literal

from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity
from ccnl_engine.engine.payroll.domain.components import (
    ScopeItem,
    _coerce,
)
from ccnl_engine.engine.payroll.domain.quality import Limitation
from ccnl_engine.engine.serialization.result_codec import _serialise_dataclass


@dataclass(frozen=True, kw_only=True)
class Coverage:
    """Computation quality and coverage metadata.

    ``consumed_rulesets`` records the exact identity of every policy consumed
    during the computation.  A ``None`` entry means a ruleset was consumed but
    its identity is absent or incomplete (treated as unverified).

    ``limitations`` records structured engine or dataset limitations that
    applied during this computation.
    """

    status: Literal["partial", "complete"]
    confidence: Literal["low", "medium", "high"]
    calculation_scope: tuple[ScopeItem, ...]
    warnings: tuple[str, ...]
    consumed_rulesets: tuple[RulesetIdentity | None, ...] = field(default_factory=tuple)
    limitations: tuple[Limitation, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict.

        Returns:
            Dict with tuples serialised as lists.
        """
        return _serialise_dataclass(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Coverage:
        """Reconstruct from a serialised dict.

        Returns:
            A new :class:`Coverage` with all fields restored.
        """
        hints = typing.get_type_hints(cls)
        kwargs: dict[str, object] = {}
        for f in dataclasses.fields(cls):
            if f.name not in data:
                continue  # use dataclass default
            if f.name == "limitations":
                raw_lims = data["limitations"]
                lims_list = raw_lims if isinstance(raw_lims, list) else []
                kwargs["limitations"] = tuple(
                    Limitation.from_dict(item)
                    for item in lims_list
                    if isinstance(item, dict)
                )
            else:
                kwargs[f.name] = _coerce(data[f.name], hints[f.name])
        return cls(**kwargs)  # type: ignore[arg-type]
