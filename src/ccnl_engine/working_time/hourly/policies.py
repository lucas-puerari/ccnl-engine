"""Hourly base of a CCNL: the monthly pay elements over its hourly divisor.

The rate an overtime hour, a supplement or an absence is paid with is, when
the caller does not state it, the hourly base of the CCNL: the monthly pay
elements its ``work_rules.time_supplements.hourly_base_method`` names,
divided by ``parameters.hourly_divisor`` in force on the day of the event.
The elements are those of the worker's level, seniority and allowances on
a full-time month (the CCNL divisor is a full-time divisor), reduced by the
apprenticeship percentage of an apprentice.

The engine derives it only from a sourced rule, never from a default:

- the CCNL ``hourly_base_provenance`` is ``verified``;
- a divisor is in force on the day;
- the full-time week of the employment, when stated, is the one the divisor
  belongs to (``hourly_divisor_weekly_hours``): Turismo art. 151 divides by
  190 for 44 hours, not by 172.

Otherwise the event needs the caller's value and the run is rejected with
:class:`~ccnl_engine.errors.InvalidInputError` naming the reason.

Individual elements (``Employment.individual_elements``: superminimi,
aumenti di merito, assegni ad personam) never enter the hourly base, though
some CCNLs count them (metalmeccanici, chimica art. 15 punto 1, terziario
art. 208).  Every derived decision reports ``individual_elements``
``not_included``: a worker who has them under such a CCNL states the rate.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, NoReturn

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus
from ccnl_engine.working_time.supplement.models import HourlyBaseMethod

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.provenance.source.models import SourceLocation
    from ccnl_engine.working_time.models import TimeSupplements

__all__ = ["BASE_PATH", "HourlyBase", "HourlyTerms", "reject_underived"]

#: Path of the hourly base method in a CCNL file.
BASE_PATH = "work_rules.time_supplements.hourly_base_method"


@dataclass(frozen=True)
class HourlyBase:
    """The hourly rate of a CCNL on one day and what it is made of.

    Attributes:
        rate: ``monthly / divisor``, unrounded.
        monthly: Sum of the monthly pay elements.
        divisor: Hourly divisor of the CCNL in force on the day.
        method: The elements the CCNL names.
        components: Each element and its full-time monthly amount.
    """

    rate: Decimal
    monthly: Decimal
    divisor: Decimal
    method: HourlyBaseMethod
    components: tuple[tuple[str, Decimal], ...]

    def inputs(self) -> dict[str, Decimal | str]:
        """Return the decision inputs that show how the rate was built.

        Returns:
            The method, each component, the monthly sum, the divisor, the
            rate and the individual elements left out.
        """
        return {
            "hourly_base_method": self.method.value,
            **{f"hourly_base[{name}]": amount for name, amount in self.components},
            "hourly_base_monthly": self.monthly,
            "hourly_divisor": self.divisor,
            "hourly_base_rate": self.rate,
            "individual_elements": "not_included",
        }


def _components(
    chain: MonthlyPayChain, method: HourlyBaseMethod
) -> tuple[tuple[str, Decimal], ...]:
    """Return the monthly pay elements ``method`` names, from ``chain``.

    Returns:
        The base salary, then the seniority, then each cash allowance, as
        far as the method reaches.
    """
    found: list[tuple[str, Decimal]] = [("base_salary", chain.base)]
    if method is HourlyBaseMethod.MINIMO_TABELLARE:
        return tuple(found)
    found.append(("seniority", chain.seniority))
    if method is HourlyBaseMethod.GROSS_INCL_ALLOWANCES:
        found.extend((a.code, v) for a, v in chain.allowances if not a.in_kind)
    return tuple(found)


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
    def base_source(self) -> SourceLocation | None:
        """Location of the hourly base rule, when recorded."""
        supplements = self.supplements
        record = None if supplements is None else supplements.hourly_base_provenance
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
        if week is not None and stated is not None and stated != week:
            return (
                f"the CCNL ({self.ruleset}) hourly divisor is the one of a "
                f"{week}-hour week and the employment states a full-time week "
                f"of {stated} hours, whose divisor is not modelled"
            )
        period = self.ccnl.parameters.hourly_divisor.period_at(day)
        if period is None or period.value is None:
            return f"the CCNL ({self.ruleset}) has no hourly divisor on {day}"
        return self.ccnl, self.chain, supplements, period.value

    def base(
        self,
        day: date,
        field: str,
        feature: str,
        method: HourlyBaseMethod | None = None,
    ) -> HourlyBase:
        """Return the hourly base on ``day``.

        Args:
            day: Day of the event; the divisor in force on it applies.
            field: Caller field the base stands in for, named in the error.
            feature: Capability of the event, named in the error.
            method: Elements of a band with its own base; ``None`` for the
                hourly base of the CCNL.

        Returns:
            The hourly base; the event is rejected (``reject_underived``)
            when it cannot be derived on ``day``.
        """
        parts = self._parts(day)
        if isinstance(parts, str):
            reject_underived(field, feature, day, parts)
        _, chain, supplements, divisor = parts
        named = method or supplements.hourly_base_method
        components = _components(chain, named)
        monthly = sum((v for _, v in components), Decimal(0))
        return HourlyBase(monthly / divisor, monthly, divisor, named, components)


def reject_underived(field: str, feature: str, day: date, reason: str) -> NoReturn:
    """Reject an event value the caller left out and the engine cannot derive.

    Raises:
        InvalidInputError: Naming the field, the day and the reason, with
            the remediation to pass the value.
    """
    msg = f"{field} on {day.isoformat()} is not stated and {reason}"
    raise InvalidInputError(
        msg,
        field=field,
        feature=feature,
        remediation=f"Pass {field}: the engine does not derive it here.",
    )
