"""CCNL overtime bands and the rule identity by which they are cited."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.provenance.source.rule.models import RuleProvenance
    from ccnl_engine.working_time.models import OvertimeBand
    from ccnl_engine.working_time.overtime.quota import OvertimeExemptQuota
    from ccnl_engine.working_time.overtime.supplementary import (
        SupplementaryExcess,
    )


@dataclass(frozen=True)
class CCNLOvertimeBands:
    """The overtime bands of a CCNL and the rule identity they are cited by.

    Attributes:
        bands: Time-supplement bands of the CCNL that apply to the worker's
            level, empty when it has none. They identify the full premium
            before a worker's rest election changes its immediate cash value.
        bank_share: Fraction of the applicable overtime premium paid now
            when the worker banks the base hour for later rest. Absent when
            the CCNL does not define such a rule. This is not a bank balance
            and carries neither a rest date nor a payout date.
        bank_source: Provenance of that fraction, separate from the source
            of each ordinary overtime band. It is cited in the decision
            for the cash premium on banked hours.
        ruleset: Ruleset identifier of the CCNL.
        version: Ruleset version.
        exempt_quota: Extra premium past the yearly exempt quota, if any.
        headcount: Employer headcount, which chooses that quota.
        ccnl_id: Identifier of the CCNL, which scopes its limitations.
        supplementary_excess: Rate of the supplementary hours past a yearly
            share of the agreed hours, if any.
    """

    bands: tuple[OvertimeBand, ...] = ()
    bank_share: Decimal | None = None
    bank_source: RuleProvenance | None = None
    ruleset: str = "ccnl"
    version: str = "none"
    exempt_quota: OvertimeExemptQuota | None = None
    headcount: int | None = None
    ccnl_id: str = "ccnl"
    supplementary_excess: SupplementaryExcess | None = None

    @classmethod
    def of(
        cls,
        ccnl: CCNL,
        year: int,
        level_code: str | None = None,
        headcount: int | None = None,
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
        share = None if supplements is None else supplements.overtime_bank_share
        source = None if supplements is None else supplements.overtime_bank_provenance
        quota = None if supplements is None else supplements.overtime_exempt_quota
        excess = None if supplements is None else supplements.supplementary_excess
        if ccnl.ruleset is not None:
            ruleset, version = ccnl.ruleset.id, ccnl.ruleset.version
        else:
            ruleset, version = f"ccnl/{ccnl.meta.ccnl_id}", str(year)
        return cls(
            bands,
            share,
            source,
            ruleset,
            version,
            quota,
            headcount,
            ccnl.meta.ccnl_id,
            excess,
        )

    @classmethod
    def of_run(cls, ctx: RunContext) -> CCNLOvertimeBands:
        """Return the bands of the run's CCNL, level and employer.

        Returns:
            :meth:`of` with the competence year, the level and the headcount.
        """
        return cls.of(
            ctx.contract.ccnl,
            ctx.contract.tctx.competence.year,
            ctx.request.level_code,
            ctx.request.employer.headcount.value,
        )

    def rule_of(self, band: OvertimeBand) -> str:
        """Return the rule identifier of ``band``.

        Returns:
            ``<ruleset>:work_rules.time_supplements.overtime_bands[<code>]``.
        """
        return f"{self.ruleset}:work_rules.time_supplements.overtime_bands[{band.code}]"
