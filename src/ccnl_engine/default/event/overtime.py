"""Defaults of the yearly facts of an overtime event."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import FactEnforcement, absence_is_fact, requires_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["OVERTIME_DEFAULTS"]

#: Classification of the yearly facts of an overtime event.
OVERTIME_DEFAULTS: Mapping[str, FieldDefault] = {
    "OvertimeEvent.exempt_quota_hours_before": absence_is_fact(
        "agreed overtime, outside the regime of the quote esenti: no premium "
        "past the yearly exempt quota"
    ),
    "OvertimeEvent.in_periodic_shift": requires_fact(
        "overtime",
        "event.in_periodic_shift",
        FactEnforcement.REPORTED,
        "unknown turnista status: the overtime takes the bands of the non "
        "turnisti; an event in the regime of the quote esenti in a firm up to "
        "the CCNL headcount has a missing_fact in_periodic_shift",
    ),
    "OvertimeEvent.supplementary_hours_before": requires_fact(
        "overtime",
        "event.supplementary_hours_before",
        FactEnforcement.REPORTED,
        "unknown earlier supplementary hours of the year: a CCNL whose rate "
        "rises past a share of the annual part-time hours pays the base band "
        "with a missing_fact supplementary_hours_before",
    ),
    "OvertimeEvent.agreed_annual_hours": requires_fact(
        "overtime",
        "event.agreed_annual_hours",
        FactEnforcement.REPORTED,
        "unknown annual part-time hours: the share past which the "
        "supplementary rate rises is not known, the base band is paid with a "
        "missing_fact agreed_annual_hours",
    ),
}
