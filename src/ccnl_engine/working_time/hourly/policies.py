"""Hourly base of a CCNL: the monthly pay elements over its hourly divisor.

The rate an overtime hour, a supplement or an absence is paid with is, when
the caller does not state it, the hourly base of the CCNL: the monthly pay
elements its ``work_rules.time_supplements.hourly_base_method`` names,
divided by the worker's level-specific ``hourly_divisor`` when present, or
``parameters.hourly_divisor`` otherwise, in force on the day of the event.
A sourced level ``hourly_base_method`` can also select different pay elements.
The elements are those of the worker's level, seniority and allowances on
a full-time month (the CCNL divisor is a full-time divisor), reduced by the
apprenticeship percentage of an apprentice.

The engine derives it only from a sourced rule, never from a default:

- the CCNL or level ``hourly_base_provenance`` is ``verified``;
- a divisor is in force on the day;
- the full-time week of the employment, when stated, is the one the divisor
  belongs to (``hourly_divisor_weekly_hours``), after ``week_divisors`` swapped
  in its own (Turismo art. 151: 190 for 44 hours, not 172).

A sourced sub-sector hourly minimum instead supplies a direct hourly floor:
it is never derived by dividing another sub-sector's monthly wage. A date
without a sourced hourly floor requires the caller's contractual hourly rate.

Otherwise the event needs the caller's value and the run is rejected with
:class:`~ccnl_engine.errors.MissingRuleError` naming the reason.

The individual elements of the worker (``Employment.individual_elements``:
superminimi, aumenti di merito, assegni ad personam) enter the base as the
CCNL ``time_supplements.individual_elements`` rule says: in the hour and in
its supplements, in neither, or in the hour only (Commercio art. 149: the
hour at the retribuzione di fatto, the maggiorazione on the normale
retribuzione).  A worker with individual elements under a CCNL whose rule
is not verified has no derived base.  Every derived decision reports
``individual_elements``: ``included``, ``not_included`` or ``none``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, NoReturn

from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus
from ccnl_engine.working_time.hourly.base import HourlyBase
from ccnl_engine.working_time.hourly.components import (
    components,
    individual,
    level_method,
    week_mismatch,
)
from ccnl_engine.working_time.hourly.direct import direct_hourly_base
from ccnl_engine.working_time.supplement.models import (
    HourlyBaseMethod,
    IndividualInBase,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.models import Level
    from ccnl_engine.provenance.source.models import SourceLocation
    from ccnl_engine.working_time.models import TimeSupplements

__all__ = ["BASE_PATH", "HourlyBase", "HourlyTerms", "Unstated", "reject_underived"]

#: Path of the hourly base method in a CCNL file.
BASE_PATH = "work_rules.time_supplements.hourly_base_method"


@dataclass(frozen=True)
class HourlyTerms:
    """What the hourly base of a run's worker is derived from.

    The defaults derive nothing: every event needs the caller's value.

    Attributes:
        ccnl: The CCNL of the run.
        chain: Full-time pay chain of the worker on the competence date.
        level_code: Level of the worker, selecting the bands of a level.
        roles: Roles of the worker; ``None`` when not stated.
        full_time_weekly_hours: Full-time week of the employment, when
            stated.
        part_time: Whether the employment is part time.
        ruleset: Ruleset identifier of the CCNL.
        version: Ruleset version.
    """

    ccnl: CCNL | None = None
    chain: MonthlyPayChain | None = None
    level_code: str | None = None
    roles: frozenset[str] | None = None
    full_time_weekly_hours: Decimal | None = None
    part_time: bool = False
    ruleset: str = "ccnl"
    version: str = "none"

    @property
    def supplements(self) -> TimeSupplements | None:
        """The time-supplement rules of the CCNL, ``None`` without them."""
        rules = None if self.ccnl is None else self.ccnl.work_rules
        return None if rules is None else rules.time_supplements

    @property
    def level(self) -> Level | None:
        """The worker's level, if the contract and code are known.

        Returns:
            The matching level, or ``None`` without it.
        """
        if self.ccnl is None:
            return None
        return next((lv for lv in self.ccnl.levels if lv.code == self.level_code), None)

    @property
    def base_source(self) -> SourceLocation | None:
        """Location of the hourly base rule, when recorded."""
        supplements = self.supplements
        record = None if supplements is None else supplements.hourly_base_provenance
        level = self.level
        if level is not None and level.hourly_base_provenance is not None:
            record = level.hourly_base_provenance
        return None if record is None else record.location

    def rule_of(self, path: str) -> str:
        """Return the rule identifier of ``path`` in the CCNL.

        Returns:
            ``<ruleset>:<path>``.
        """
        return f"{self.ruleset}:{path}"

    def _parts(
        self, day: date
    ) -> tuple[CCNL, MonthlyPayChain, TimeSupplements, Decimal] | str:
        """Return what the hourly base on ``day`` is built from, or why not.

        Returns:
            The CCNL, the chain, the supplement rules and the divisor, or the
            reason the base cannot be derived.
        """
        supplements = self.supplements
        record = None if supplements is None else supplements.hourly_base_provenance
        level = self.level
        if level is not None and level.hourly_base_provenance is not None:
            record = level.hourly_base_provenance
        if (
            self.ccnl is None
            or self.chain is None
            or supplements is None
            or record is None
            or record.status is not ProvenanceStatus.VERIFIED
        ):
            return f"the CCNL ({self.ruleset}) has no verified hourly base"
        week = supplements.hourly_divisor_weekly_hours
        stated = self.full_time_weekly_hours
        if week_mismatch(level, week, stated):
            return (
                f"the CCNL ({self.ruleset}) hourly divisor is the one of a "
                f"{week}-hour week and the employment states a full-time week "
                f"of {stated} hours, whose divisor is not modelled"
            )
        series = (
            level.hourly_divisor
            if level is not None and level.hourly_divisor is not None
            else self.ccnl.parameters.hourly_divisor
        )
        period = series.period_at(day)
        if period is None or period.value is None:
            return f"the CCNL ({self.ruleset}) has no hourly divisor on {day}"
        return self.ccnl, self.chain, supplements, period.value

    def base(
        self,
        day: date,
        field: str,
        feature: str,
        method: HourlyBaseMethod | None = None,
        *,
        supplement: bool = False,
    ) -> HourlyBase:
        """Return the hourly base on ``day``.

        Args:
            day: Day of the event; the divisor in force on it applies.
            field: Caller field the base stands in for, named in the error.
            feature: Capability of the event, named in the error.
            method: Elements of a band with its own base; ``None`` for the
                hourly base of the CCNL.
            supplement: Whether the base is that of a maggiorazione, which a
                CCNL of :attr:`IndividualInBase.HOUR_ONLY` computes without
                the individual elements.

        Returns:
            The hourly base; the event is rejected (``reject_underived``)
            when it cannot be derived on ``day``, or when the worker has
            individual elements and the CCNL rule on them is not verified.
            A directly printed hourly floor is used only for dates and levels
            explicitly present in the sub-sector's table.
        """
        direct = direct_hourly_base(
            self.supplements,
            self.level_code,
            self.chain,
            day,
            field,
            feature,
            method,
            reject_underived,
        )
        if direct is not None:
            return direct
        parts = self._parts(day)
        if isinstance(parts, str):
            reject_underived(field, feature, day, parts)
        _, chain, supplements, divisor = parts
        named = method or level_method(self.level, supplements.hourly_base_method)
        parts_of_base = components(chain, named, supplements.hourly_base_excluded)
        personal = individual(chain)
        state = "none"
        if personal:
            rule = supplements.individual_elements
            if rule is None or rule.provenance.status is not ProvenanceStatus.VERIFIED:
                reject_underived(
                    field,
                    feature,
                    day,
                    f"the CCNL ({self.ruleset}) does not say whether the "
                    "individual elements of the worker enter the hourly base",
                )
            where = rule.in_hourly_base
            included = where is IndividualInBase.INCLUDED or (
                where is IndividualInBase.HOUR_ONLY and not supplement
            )
            state = "included" if included else "not_included"
            parts_of_base += personal if included else ()
        monthly = sum((v for _, v in parts_of_base), Decimal(0))
        return HourlyBase(
            monthly / divisor, monthly, divisor, named, parts_of_base, state
        )

    @property
    def hour_only(self) -> bool:
        """Whether the maggiorazione leaves the individual elements out."""
        supplements = self.supplements
        rule = None if supplements is None else supplements.individual_elements
        return rule is not None and rule.in_hourly_base is IndividualInBase.HOUR_ONLY


@dataclass(frozen=True)
class Unstated:
    """Why a value is not derived: an input (``field``) left out, and why."""

    field: str
    reason: str


def reject_underived(
    field: str, feature: str, day: date, reason: str | Unstated
) -> NoReturn:
    """Reject an event value the caller left out and the engine cannot derive.

    Raises:
        InvalidInputError: When ``reason`` is :class:`Unstated`, naming it.
        MissingRuleError: Otherwise: the rule is missing, and passing the
            value is the workaround its remediation names.
    """
    if isinstance(reason, Unstated):
        msg = f"{field} on {day} is not stated and {reason.reason}"
        remedy = f"Pass {reason.field}, or {field}."
        raise InvalidInputError(
            msg, field=reason.field, feature=feature, remediation=remedy
        )
    msg = f"{reason}, and {field} is not stated"
    raise MissingRuleError(
        msg,
        as_of=day,
        feature=feature,
        remediation=f"Pass {field}: the engine does not derive it here.",
    )
