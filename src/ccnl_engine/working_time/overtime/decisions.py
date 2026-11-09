"""Decisions citing the overtime band that supplied a paid rate."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.event.facade import OvertimeEvent
    from ccnl_engine.working_time.overtime.models import CCNLOvertimeBands
    from ccnl_engine.working_time.overtime.policies import OvertimeRate

CCNL_BAND_APPLIED = "ccnl_overtime_band_applied"


def band_decision(
    event: OvertimeEvent, rate: OvertimeRate, bands: CCNLOvertimeBands, amount: Decimal
) -> CalculationDecision | None:
    """Return the decision of a multiplier derived from the CCNL band.

    Returns:
        An ``overtime`` decision citing the first applied band and listing
        any resolved weekly slices, provisional when tiers were left out;
        ``None`` for a caller multiplier.
    """
    band = rate.band
    if not rate.derived or band is None:
        return None
    provenance = band.provenance
    paid: dict[str, Decimal | str] = (
        {"band_hourly_amount": rate.hourly_amount}
        if rate.hourly_amount is not None
        else {"band_supplement": rate.supplement or Decimal(0)}
    )
    if rate.weekly_slices:
        paid["weekly_tiers"] = ", ".join(
            f"{b.code}: {hours}h at {1 + supplement}"
            for b, supplement, hours in rate.weekly_slices
        )
    return CalculationDecision(
        capability="overtime",
        status=CalculationStatus.PROVISIONAL if rate.tiers else CalculationStatus.FINAL,
        reason_code=CCNL_BAND_APPLIED,
        rule=bands.rule_of(band),
        rule_version=bands.version,
        inputs={
            "kind": event.kind.value,
            "band_code": band.code,
            **paid,
            "multiplier": rate.multiplier,
            "hours": event.hours,
            "hourly_rate": (
                "not_stated" if event.hourly_rate is None else event.hourly_rate
            ),
        },
        source=None if provenance is None else provenance.location,
        amount=amount,
    )
