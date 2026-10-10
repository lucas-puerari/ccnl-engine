"""Defaults of the work events of :mod:`ccnl_engine.events`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.period.models_default import (
    FactEnforcement,
    absence_is_fact,
    requires_fact,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.period.models_default import FieldDefault

__all__ = ["EVENT_DEFAULTS"]

#: Classification of each defaulted field of the work events.
EVENT_DEFAULTS: Mapping[str, FieldDefault] = {
    "AbsenceEvent.end_date": absence_is_fact("a one-day absence"),
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
    "BonusEvent.kind": absence_is_fact(
        "an ordinary bonus taxed as income; a preferential kind is declared"
    ),
    "BonusEvent.agreement_signed_on": requires_fact(
        "rinnovo_substitute_tax",
        "event.agreement_signed_on",
        FactEnforcement.REPORTED,
        "unknown signing date: the renewal regime is undetermined, with a blocker",
    ),
    "OvertimeEvent.multiplier": absence_is_fact(
        "the multiplier of the CCNL band applies"
    ),
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
    "SicknessEpisode.short_absence_exempt": requires_fact(
        "sickness",
        "event.short_absence_exempt",
        FactEnforcement.REPORTED,
        "unknown exemption: a short absence the CCNL could pay less has a "
        "missing_fact short_absence_exempt blocker and is paid unreduced",
    ),
}
