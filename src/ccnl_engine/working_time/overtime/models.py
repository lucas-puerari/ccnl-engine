"""CCNL overtime bands and the rule identity by which they are cited."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import MissingRequiredFactError

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.provenance.source.rule.models import RuleProvenance
    from ccnl_engine.working_time.inputs import OvertimeEvent
    from ccnl_engine.working_time.models import OvertimeBand
    from ccnl_engine.working_time.overtime.multiweek import MultiweekExcess
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
        multiweek_excess: Points added to the multi-week premiums past a
            threshold of hours, if any.
        unstated_role_kinds: Work kinds a band of a role pays apart, when the
            worker's roles are not stated: an event of them is blocked.
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
    multiweek_excess: MultiweekExcess | None = None
    unstated_role_kinds: frozenset[str] = frozenset()

    @classmethod
    def of(
        cls,
        ccnl: CCNL,
        year: int,
        level_code: str | None = None,
        headcount: int | None = None,
        roles: frozenset[str] | None = frozenset(),
    ) -> CCNLOvertimeBands:
        """Return the bands of ``ccnl`` that apply to ``level_code``.

        A band naming no level applies to every level; without a level only
        those bands are kept.  A band of a role replaces, for a worker of
        that role, the band of the same kinds and thresholds
        (:func:`for_roles`).

        Returns:
            The bands with the CCNL ruleset, or its slug and ``year``.
        """
        rules = ccnl.work_rules
        supplements = None if rules is None else rules.time_supplements
        every = () if supplements is None else supplements.overtime_bands
        bands, unstated = for_roles(
            tuple(b for b in every if not b.levels or level_code in b.levels), roles
        )
        share = None if supplements is None else supplements.overtime_bank_share
        source = None if supplements is None else supplements.overtime_bank_provenance
        quota = None if supplements is None else supplements.overtime_exempt_quota
        excess = None if supplements is None else supplements.supplementary_excess
        multiweek = None if supplements is None else supplements.multiweek_excess
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
            multiweek,
            unstated,
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
            ctx.request.roles,
        )

    def require_roles(self, event: OvertimeEvent) -> None:
        """Block an event without a multiplier a band of a role pays apart.

        Raises:
            MissingRequiredFactError: When the worker's roles are not stated.
        """
        kind = event.kind.value
        if event.multiplier is None and kind in self.unstated_role_kinds:
            msg = (
                f"the CCNL ({self.ccnl_id}) pays {kind} overtime apart for a "
                "role and Employment.roles is not stated"
            )
            raise MissingRequiredFactError(
                msg,
                feature="overtime",
                ruleset=self.ccnl_id,
                remediation="State Employment.roles (an empty set for none).",
            )

    def rule_of(self, band: OvertimeBand) -> str:
        """Return the rule identifier of ``band``.

        Returns:
            ``<ruleset>:work_rules.time_supplements.overtime_bands[<code>]``.
        """
        return f"{self.ruleset}:work_rules.time_supplements.overtime_bands[{band.code}]"


def _key(band: OvertimeBand) -> tuple[object, ...]:
    return (
        frozenset(band.applies_to_kinds),
        band.hour_threshold_per_day,
        band.hour_threshold_per_week,
    )


def for_roles(
    bands: tuple[OvertimeBand, ...], roles: frozenset[str] | None
) -> tuple[tuple[OvertimeBand, ...], frozenset[str]]:
    """Return the bands of a worker holding ``roles``.

    Returns:
        The bands of no role, less those a band of a held role replaces (the
        same kinds and thresholds), with the bands of the held roles; and,
        when ``roles`` is not stated, the work kinds the bands of a role pay,
        whose events are then blocked.
    """
    named = [b for b in bands if b.role is not None]
    general = tuple(b for b in bands if b.role is None)
    if not named:
        return bands, frozenset()
    if roles is None:
        return general, frozenset(k.value for b in named for k in b.applies_to_kinds)
    held = tuple(b for b in named if b.role in roles)
    replaced = {_key(b) for b in held}
    return tuple(b for b in general if _key(b) not in replaced) + held, frozenset()
