"""Defaults of the work events of :mod:`ccnl_engine.events`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.event.sickness import SICKNESS_DEFAULTS
from ccnl_engine.default.event.travel import TRAVEL_DEFAULTS
from ccnl_engine.default.models import (
    FactEnforcement,
    absence_is_fact,
    requires_fact,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["EVENT_DEFAULTS"]

#: Classification of each defaulted field of the work events.
_FROM_CCNL = (
    "the value the CCNL sets, derived from its sourced rule; where the CCNL "
    "sets none the engine applies, the event is rejected"
)
_SUPPLEMENT_HOURS = (
    "read only without supplement_amount, which then requires it to derive "
    "the CCNL supplement"
)

#: Classification of each defaulted field of the work events.
EVENT_DEFAULTS: Mapping[str, FieldDefault] = {
    "AbsenceEvent.end_date": absence_is_fact("a one-day absence"),
    "AbsenceEvent.hourly_rate": absence_is_fact(_FROM_CCNL),
    "AbsenceEvent.working_days": absence_is_fact(
        "an absence of hours; a CCNL that deducts whole days then needs the "
        "caller's hourly_rate"
    ),
    "OvertimeEvent.hourly_rate": absence_is_fact(_FROM_CCNL),
    "OvertimeEvent.non_occasional": absence_is_fact("occasional overtime"),
    "OvertimeEvent.banked": absence_is_fact(
        "no election to bank overtime: pay the ordinary overtime hour and "
        "its full premium; a rest election must be stated by the caller"
    ),
    "NightShiftEvent.supplement_amount": absence_is_fact(_FROM_CCNL),
    "NightShiftEvent.hours": absence_is_fact(_SUPPLEMENT_HOURS),
    "NightShiftEvent.before_22": absence_is_fact(
        "night hours from 22:00; hours before it are a fact of the timesheet "
        "the event records"
    ),
    "HolidayWorkEvent.supplement_amount": absence_is_fact(_FROM_CCNL),
    "HolidayWorkEvent.hours": absence_is_fact(_SUPPLEMENT_HOURS),
    "HolidayWorkEvent.kind": absence_is_fact(
        "work on a public holiday; a Sunday, rest day or compensatory rest is "
        "a fact of the timesheet the event records"
    ),
    "HolidayWorkEvent.in_periodic_shift": requires_fact(
        "holiday_work",
        "event.in_periodic_shift",
        FactEnforcement.REPORTED,
        "unknown turnista (rotating-shift worker) status: only a CCNL band "
        "excluding shift workers requires it when deriving its supplement; "
        "other bands do not, regardless of the turn of these particular hours",
    ),
    "ShiftWorkEvent.supplement_amount": absence_is_fact(_FROM_CCNL),
    "ShiftWorkEvent.hours": absence_is_fact(_SUPPLEMENT_HOURS),
    "ShiftWorkEvent.kind": absence_is_fact(
        "read only without supplement_amount, which then requires it to "
        "choose the CCNL shift band"
    ),
    "AbsenceEvent.suspends_accrual": requires_fact(
        "absence",
        "event.suspends_accrual",
        FactEnforcement.REPORTED,
        "unknown suspension: the days count as accruing, and a rateo of an "
        "extra month they could change has a missing_fact suspends_accrual "
        "blocker",
    ),
    "AbsenceEvent.no_pay_due": requires_fact(
        "absence",
        "event.no_pay_due",
        FactEnforcement.REPORTED,
        "unknown pay of the days: they stay in the days of the art. 13 TUIR "
        "deductions, and a withholding run has a missing_fact no_pay_due "
        "blocker",
    ),
    "ArrearsEvent.reference_period": requires_fact(
        "contract_renewal_arrears",
        "event.reference_period",
        FactEnforcement.REPORTED,
        "unknown reference year: separate or ordinary taxation (art. 17 c. 1 "
        "lett. b TUIR) is undetermined, with a blocker",
    ),
    "ArrearsEvent.separate_tax_rate": absence_is_fact(
        "no rate from the caller: the engine computes it from "
        "PriorYearTaxFacts.net_income_biennio (art. 21 TUIR)"
    ),
    "ArrearsEvent.unused_deductions": requires_fact(
        "contract_renewal_arrears",
        "event.unused_deductions",
        FactEnforcement.PENDING,
        "unknown unused deductions: the separate tax is not reduced (art. 21 "
        "c. 4 TUIR), with the arrears_unused_deductions limitation",
    ),
    # The fact the arrears rate is computed from, with the event that reads it.
    "PriorYearTaxFacts.special_supplement_requested": absence_is_fact(
        "no written request (L. 199/2025 art. 1 c. 20): no supplement is paid"
    ),
    "PriorYearTaxFacts.net_income_biennio": requires_fact(
        "contract_renewal_arrears",
        "prior_year.net_income_biennio",
        FactEnforcement.REPORTED,
        "unknown income of the two years before: arrears of an earlier year "
        "without a caller rate have no separate tax, with a blocker",
    ),
    "BonusEvent.kind": absence_is_fact(
        "an ordinary bonus taxed as income; a preferential kind is declared"
    ),
    "BonusEvent.agreement_signed_on": requires_fact(
        "rinnovo_substitute_tax",
        "event.agreement_signed_on",
        FactEnforcement.REPORTED,
        "unknown signing date: the renewal regime is undetermined, with a blocker",
    ),
    "OvertimeEvent.multiplier": absence_is_fact("the CCNL band multiplier"),
    "OvertimeEvent.kind": absence_is_fact(
        "weekday overtime; a night or holiday band is a fact of the timesheet "
        "the event records"
    ),
    "SickLeaveEvent.sick_days": absence_is_fact(
        "a one-day spell of the caller-supplied amount"
    ),
    "SickLeaveEvent.waiting_period_days": absence_is_fact(
        "no waiting day is deducted from the caller-supplied amount"
    ),
    "SicknessEpisode.relapse_of": absence_is_fact(
        "a new episode; a relapse is stated by the medical certificate"
    ),
    "StandbyEvent.calls": absence_is_fact(
        "no call followed by an intervention; each is a fact of the standby log"
    ),
    "TerminationTFREvent.amount": absence_is_fact(
        "the engine computes the TFR due: the fund, the quotas of the year and "
        "the revaluation (art. 2120 c.c.)"
    ),
    "TerminationTFREvent.separate_tax_rate": absence_is_fact(
        "the engine computes the average rate of the reference income (art. 19 "
        "c. 1 TUIR)"
    ),
    **TRAVEL_DEFAULTS,
    "SicknessEpisode.hospital_stays": requires_fact(
        "sickness",
        "event.hospital_stays",
        FactEnforcement.REPORTED,
        "unknown hospital stays: the reduced days of a CCNL that pays long "
        "stays in full are paid reduced, with a provisional "
        "sickness_hospital_stays_unknown issue",
    ),
    "SicknessEpisode.inps_base": requires_fact(
        "sickness",
        "event.inps_base",
        FactEnforcement.REPORTED,
        "unknown pay of the month before the illness: the INPS share is "
        "computed on the CCNL daily quota, with a missing_fact inps_base "
        "blocker",
    ),
    "InpsSicknessBase.paid_days": requires_fact(
        "sickness",
        "event.inps_base.paid_days",
        FactEnforcement.REPORTED,
        "an impiegato who worked the whole month before the illness; an "
        "operaio divides by the days, so without them the INPS share is "
        "computed on the CCNL daily quota, with a missing_fact inps_base "
        "blocker",
    ),
    "InpsSicknessBase.full_month_pay": requires_fact(
        "sickness",
        "event.inps_base.full_month_pay",
        FactEnforcement.REPORTED,
        "a month worked in full; an impiegato who did not work it all needs "
        "the pay of a whole month, so without it the INPS share is computed "
        "on the CCNL daily quota, with a missing_fact inps_base blocker",
    ),
    "MaternityLeaveEvent.maternity_base_pay": requires_fact(
        "maternity_leave",
        "event.maternity_base_pay",
        FactEnforcement.REPORTED,
        "unknown pay of the month before the leave: the indemnity is computed "
        "on the pay of the run, with a missing_fact maternity_base_pay "
        "blocker",
    ),
    "ParentalLeaveEvent.parental_base_pay": requires_fact(
        "parental_leave",
        "event.parental_base_pay",
        FactEnforcement.REPORTED,
        "Unknown previous-month pay: the run's pay is used provisionally.",
    ),
    "ParentalLeaveEvent.topped_up_days_before": requires_fact(
        "parental_leave",
        "event.topped_up_days_before",
        FactEnforcement.REPORTED,
        "Unknown prior supplemented days block the CCNL top-up.",
    ),
    "ParentalLeaveEvent.protection_ended_on": requires_fact(
        "parental_leave",
        "event.protection_ended_on",
        FactEnforcement.REPORTED,
        "Unknown protected leave end may change the enhanced INPS months.",
    ),
    "DisabilityPermitEvent.hours": absence_is_fact(
        "permits taken as whole days only; hours of permit are a fact of the "
        "timesheet the event records"
    ),
    "ParentalLeaveEvent.single_parent": absence_is_fact("sole parent status"),
    "HourlyParentalLeaveEvent.parental_base_pay": requires_fact(
        "parental_leave",
        "event.parental_base_pay",
        FactEnforcement.REPORTED,
        "unknown pay of the month before the leave: the indemnity is computed "
        "on the pay of the run, with a missing_fact parental_base_pay blocker",
    ),
    "HourlyParentalLeaveEvent.protection_ended_on": requires_fact(
        "parental_leave",
        "event.protection_ended_on",
        FactEnforcement.REPORTED,
        "unknown end of the maternity or paternity leave: the days are paid "
        "on the months at 80% the birth day gives, with a missing_fact "
        "protection_ended_on blocker when the end could give more",
    ),
    "HourlyParentalLeaveEvent.single_parent": absence_is_fact(
        "two parents; a sole parent is a fact of the family the event records"
    ),
    "ExtraordinaryLeaveEvent.last_fixed_pay": requires_fact(
        "extraordinary_leave",
        "event.last_fixed_pay",
        FactEnforcement.REPORTED,
        "unknown last pay before the leave: the indemnity is computed on the "
        "monthly pay of the run, with a missing_fact last_fixed_pay blocker",
    ),
    "ExtraordinaryLeaveEvent.last_month_paid_days": requires_fact(
        "extraordinary_leave",
        "event.last_month_paid_days",
        FactEnforcement.REPORTED,
        "unknown paid days: a vertical or mixed part time is paid on the "
        "full-time measure, with a provisional extraordinary_paid_days_unknown "
        "issue",
    ),
    "PaternityLeaveEvent.paternity_base_pay": requires_fact(
        "paternity_leave",
        "event.paternity_base_pay",
        FactEnforcement.REPORTED,
        "unknown pay of the month before the leave: the indemnity is computed "
        "on the pay of the run, with a missing_fact paternity_base_pay blocker",
    ),
    **SICKNESS_DEFAULTS,
}
