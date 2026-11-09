"""Contractual allowances paid for counted days of actual presence."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance


class DailyPresenceAllowance(BaseModel):
    """A daily cash rate selected by worker facts, not by monthly proration.

    ``role`` requires a stated worker role; ``excluded_role`` disqualifies a
    worker holding it. Both are generic role codes supplied by the agreement.
    ``day_kind`` selects days at work or the subset worked at the work site.
    ``exclusive_group`` prevents simultaneously paying incompatible brackets.
    Daily earnings have no additional-month payment and are not scaled by
    the worker's part-time fraction: the count already reflects attendance.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    rate: TimeSeries
    role: str | None = None
    excluded_role: str | None = None
    day_kind: Literal["work", "site"] = "work"
    exclusive_group: str | None = None
    tfr_relevant: bool = True
    provenance: RuleProvenance | None = None

    def applies(self, roles: frozenset[str]) -> bool:
        """Whether the stated worker facts select this allowance.

        Returns:
            True when the required role is held and the exclusion absent.
        """
        return (self.role is None or self.role in roles) and (
            self.excluded_role is None or self.excluded_role not in roles
        )
