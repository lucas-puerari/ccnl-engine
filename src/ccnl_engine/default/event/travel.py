"""Defaults of the fields of :class:`~ccnl_engine.events.TravelAllowanceEvent`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.default.models import absence_is_fact

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["TRAVEL_DEFAULTS"]

#: Classification of each defaulted field of a trasferta.
TRAVEL_DEFAULTS: Mapping[str, FieldDefault] = {
    "TravelAllowanceEvent.daily_amount": absence_is_fact(
        "the CCNL amount of the hours away; an amount of the employer's "
        "policy is a fact the event records"
    ),
    "TravelAllowanceEvent.hours_away": absence_is_fact(
        "read only without daily_amount, which then requires it"
    ),
    "TravelAllowanceEvent.tfr_base": absence_is_fact(
        "the TFR rule of the CCNL; a CCNL that states none (Studi art. 115) "
        "requires it on the event, which is otherwise rejected"
    ),
    "TravelAllowanceEvent.abroad": absence_is_fact(
        "a trasferta in Italy; abroad is a fact the event records"
    ),
    "TravelAllowanceEvent.trasfertista": absence_is_fact(
        "an ordinary trasferta; a worker bound to always different places "
        "is a fact of the contract"
    ),
    "TravelAllowanceEvent.mission_hours": absence_is_fact(
        "read only by a CCNL that sets the diaria by mission duration "
        "(Studi art. 115) and without daily_amount, which then requires it"
    ),
    "TravelAllowanceEvent.habitual_travel": absence_is_fact(
        "occasional travel; travel habitual to the job is a fact of the "
        "contract that lowers the diaria where the CCNL says so"
    ),
    "TravelAllowanceEvent.mission_over_month": absence_is_fact(
        "a mission within one calendar month; a longer one is a fact the "
        "event records, which lowers the diaria where the CCNL says so"
    ),
}
