"""Capabilities left to the caller that are not a gap of a CCNL.

The catalog marks ``caller_supplied`` a capability whose amount a caller
value may replace.  Two kinds are not a gap of the model:

- a capability the engine computes from a rule of the CCNL when the caller
  states no value (overtime, night, holiday and shift work, unjustified
  absences, travel allowance): accepted for a CCNL whose rule the engine
  computes, a gap for one that does not.  A band computes when it is a
  fixed amount, or a share of an hourly base the engine derives for every
  level (:func:`~ccnl_engine.working_time.hourly.components.derives_hourly_base`),
  and when what the hours are due is settled (``SupplementBand.paid_apart``):
  hours paid on top of the monthly pay are priced at that base;
- a capability whose amount is a fact only the employer knows (a
  second-level agreement, a territorial fund, the pay of earlier payslips):
  accepted by design, for every CCNL or, where a CCNL hands it to the
  integrative bargaining, for that CCNL (``work_rules.capability_basis``):
  the employer states the rate of its agreement once
  (``EmployerProfile.second_level_rates``) and the engine prices each event
  with it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.working_time.hourly.components import derives_hourly_base
from ccnl_engine.working_time.models import TimeSupplementKind
from ccnl_engine.working_time.supplement.models import SupplementWork

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.working_time.supplement.models import SupplementBand

__all__ = ["BY_DESIGN", "RULE_BACKED", "accepted"]

#: Capabilities supplied by the caller by design, with the reason.
BY_DESIGN: Mapping[str, str] = {
    "company_supplement": (
        "the elements of a company agreement are a fact of the employer "
        "(EmployerProfile.second_level_elements)"
    ),
    "territorial_supplement": (
        "the elements of a territorial agreement are a fact of the employer "
        "(EmployerProfile.second_level_elements)"
    ),
    "bilateral_funds": (
        "the funds the CCNL sets are computed by contractual_funds; the event "
        "carries a territorial or company fund the bundle does not hold"
    ),
    "contract_renewal_arrears": (
        "the arrears are the difference from what earlier payslips paid, a "
        "fact of the employer's payroll; the una tantum the CCNL sets is "
        "computed by una_tantum"
    ),
}

_NIGHT = frozenset({SupplementWork.NIGHT, SupplementWork.NIGHT_EARLY})
_HOLIDAY = frozenset({
    SupplementWork.HOLIDAY,
    SupplementWork.HOLIDAY_COMPENSATORY_REST,
    SupplementWork.SUNDAY,
    SupplementWork.REST_DAY,
    SupplementWork.NIGHT_HOLIDAY,
    SupplementWork.NIGHT_HOLIDAY_COMPENSATORY_REST,
    SupplementWork.NIGHT_HOLIDAY_SHIFT,
    SupplementWork.NIGHT_HOLIDAY_SHIFT_COMPENSATORY_REST,
})
_SHIFT = frozenset({SupplementWork.DAY_SHIFT, SupplementWork.NIGHT_SHIFT})


def _computes(band: SupplementBand, based: bool) -> bool:
    if band.paid_apart is None:
        return False
    if band.paid_apart:
        return based
    return band.fixed_per_hour or band.per_shift or based


def _supplements(ccnl: CCNL, works: frozenset[SupplementWork]) -> bool:
    work = ccnl.work_rules
    rules = None if work is None else work.time_supplements
    if rules is None:
        return False
    bands = [b for b in rules.supplement_bands if b.work in works]
    based = bool(bands) and derives_hourly_base(ccnl)
    return any(_computes(b, based) for b in bands)


def _overtime(ccnl: CCNL) -> bool:
    work = ccnl.work_rules
    rules = None if work is None else work.time_supplements
    if rules is None or not rules.overtime_bands:
        return False
    return derives_hourly_base(ccnl) or all(
        b.kind is not TimeSupplementKind.PERCENTAGE for b in rules.overtime_bands
    )


def _absence(ccnl: CCNL) -> bool:
    return ccnl.work_rules is not None and ccnl.work_rules.absence_rules is not None


def _travel(ccnl: CCNL) -> bool:
    return ccnl.work_rules is not None and ccnl.work_rules.travel_allowance is not None


#: Capabilities computed from a CCNL rule, with the test that the CCNL holds it.
RULE_BACKED: Mapping[str, Callable[[CCNL], bool]] = {
    "overtime": _overtime,
    "night_work": lambda ccnl: _supplements(ccnl, _NIGHT),
    "holiday_work": lambda ccnl: _supplements(ccnl, _HOLIDAY),
    "shift_work": lambda ccnl: _supplements(ccnl, _SHIFT),
    "absence": _absence,
    "travel_allowance": _travel,
}


def accepted(feature: str, ccnl: CCNL) -> bool:
    """Return whether a capability left to the caller is not a gap of *ccnl*.

    Returns:
        ``True`` for a capability supplied by design, or computed from a
        rule *ccnl* holds.
    """
    if feature in BY_DESIGN:
        return True
    if ccnl.work_rules is not None and feature in ccnl.work_rules.capability_basis:
        return True
    holds = RULE_BACKED.get(feature)
    return holds is not None and holds(ccnl)
