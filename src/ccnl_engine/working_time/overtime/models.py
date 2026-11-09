"""CCNL overtime bands and the rule identity by which they are cited."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.working_time.models import OvertimeBand


@dataclass(frozen=True)
class CCNLOvertimeBands:
    """The overtime bands of a CCNL and the rule identity they are cited by.

    Attributes:
        bands: Time-supplement bands of the CCNL that apply to the worker's
            level, empty when it has none.
        ruleset: Ruleset identifier of the CCNL.
        version: Ruleset version.
    """

    bands: tuple[OvertimeBand, ...] = ()
    ruleset: str = "ccnl"
    version: str = "none"

    @classmethod
    def of(
        cls, ccnl: CCNL, year: int, level_code: str | None = None
    ) -> CCNLOvertimeBands:
        """Return the bands of ``ccnl`` that apply to ``level_code``.

        A band naming no level applies to every level; without a level only
        those bands are kept.

        Returns:
            The bands with the CCNL ruleset, or its slug and ``year``.
        """
        rules = ccnl.work_rules
        supplements = None if rules is None else rules.time_supplements
        every = () if supplements is None else supplements.overtime_bands
        bands = tuple(b for b in every if not b.levels or level_code in b.levels)
        if ccnl.ruleset is not None:
            return cls(bands, ccnl.ruleset.id, ccnl.ruleset.version)
        return cls(bands, f"ccnl/{ccnl.meta.ccnl_id}", str(year))

    def rule_of(self, band: OvertimeBand) -> str:
        """Return the rule identifier of ``band``.

        Returns:
            ``<ruleset>:work_rules.time_supplements.overtime_bands[<code>]``.
        """
        return f"{self.ruleset}:work_rules.time_supplements.overtime_bands[{band.code}]"
