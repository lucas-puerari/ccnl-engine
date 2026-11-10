"""Derive the ordinary overtime hour and restate its distinct percentage base."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.event.standard.handlers import _standard_event_gross
from ccnl_engine.working_time.hourly.policies import BASE_PATH

#: Reason of the decision of an overtime hourly rate derived from the CCNL.
HOURLY_RATE_DERIVED = "ccnl_hourly_rate_derived"

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.event.facade import OvertimeEvent
    from ccnl_engine.working_time.hourly.policies import HourlyTerms
    from ccnl_engine.working_time.overtime.policies import OvertimeRate


def _restated(multiplier: Decimal, day: date, hourly: HourlyTerms) -> Decimal:
    """Return ``multiplier`` restated on the rate of the hour.

    Commercio art. 149 pays the hour at the retribuzione di fatto (the
    individual elements included) and the maggiorazione on the normale
    retribuzione (without them): ``hours x rate x restated`` is the hour
    plus the maggiorazione on its own base.

    Returns:
        ``1 + (multiplier - 1) x normale / fatto``, unrounded.
    """
    field = "OvertimeEvent.hourly_rate"
    hour = hourly.base(day, field, "overtime")
    normale = hourly.base(day, field, "overtime", supplement=True)
    return 1 + (multiplier - 1) * normale.rate / hour.rate


def hourly_paid(
    event: OvertimeEvent, rate: OvertimeRate, hourly: HourlyTerms
) -> tuple[OvertimeEvent, list[CalculationDecision]]:
    """Price the hour and its premium on separate bases when the band says so.

    Returns:
        The paid event and any decision for a derived ordinary hourly rate.
    """
    paid = rate.paid(event)
    decisions: list[CalculationDecision] = []
    if paid.hourly_rate is None:
        base = hourly.base(event.event_date, "OvertimeEvent.hourly_rate", "overtime")
        paid = replace(paid, hourly_rate=base.rate)
        inputs = {"hours": event.hours, **base.inputs()}
        multiplier = paid.multiplier
        premium_method = (
            None if rate.derived_band is None else rate.derived_band.premium_base
        )
        if multiplier and premium_method is not None:
            premium = hourly.base(
                event.event_date,
                "OvertimeEvent.hourly_rate",
                "overtime",
                premium_method,
                supplement=True,
            )
            restated = 1 + (multiplier - 1) * premium.rate / base.rate
            paid = replace(paid, multiplier=restated)
            inputs["multiplier_on_hour"] = restated
            inputs["premium_monthly_base"] = premium.monthly
        elif base.individual == "included" and hourly.hour_only and multiplier:
            restated = _restated(multiplier, event.event_date, hourly)
            paid = replace(paid, multiplier=restated)
            inputs["multiplier_on_hour"] = restated
        decisions.append(
            CalculationDecision(
                capability="overtime",
                status=CalculationStatus.FINAL,
                reason_code=HOURLY_RATE_DERIVED,
                rule=hourly.rule_of(BASE_PATH),
                rule_version=hourly.version,
                inputs=inputs,
                source=hourly.base_source,
                amount=_standard_event_gross(paid),
            )
        )
    if (
        event.hourly_rate is not None
        and rate.derived_band is not None
        and rate.derived_band.premium_base is not None
    ):
        premium = hourly.base(
            event.event_date,
            "OvertimeEvent.hourly_rate",
            "overtime",
            rate.derived_band.premium_base,
            supplement=True,
        )
        paid = replace(
            paid,
            multiplier=1 + (rate.multiplier - 1) * premium.rate / event.hourly_rate,
        )
    return paid, decisions
