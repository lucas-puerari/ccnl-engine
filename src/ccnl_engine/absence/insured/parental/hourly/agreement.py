"""The company or territorial agreement on the parental leave by the hour.

Art. 32 c. 1-ter D.Lgs. 151/2001 applies its general criterion (half the
average daily hours, two such days a day of leave, no cumulation with the
other permits and rests of the decree) "In caso di mancata regolamentazione,
da parte della contrattazione collettiva, anche di livello aziendale": an
agreement of the company or of the territory is a fact of the employer
(``HourlyParentalLeaveEvent.local_hourly_agreement``).  When it is not
stated the run cannot tell the criterion applies; when one regulates the
leave the run holds none of its rules.
"""

from __future__ import annotations

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause

__all__ = ["AGREEMENT_UNKNOWN", "AGREEMENT_UNMODELLED", "agreement_issue"]

#: Issue of an hourly leave whose company or territorial agreement is not stated.
AGREEMENT_UNKNOWN = "parental_hourly_agreement_unknown"
#: Issue of an hourly leave a company or territorial agreement regulates.
AGREEMENT_UNMODELLED = "parental_hourly_agreement_unmodelled"
_FACT = "local_hourly_agreement"


def agreement_issue(stated: bool | None, capability: str) -> CalculationIssue | None:
    """Tell whether the general criterion of art. 32 c. 1-ter applies.

    Returns:
        ``None`` when no local agreement regulates the leave; a missing-fact
        issue when it is not stated; an issue of the rule the run does not
        hold when one does.
    """
    if stated is False:
        return None
    if stated is None:
        return CalculationIssue(
            code=AGREEMENT_UNKNOWN,
            message=(
                "state local_hourly_agreement: whether a company or territorial "
                "agreement regulates the parental leave by the hour (art. 32 c. "
                "1-ter D.Lgs. 151/2001 applies its criterion only without one)"
            ),
            status=CalculationStatus.INCOMPLETE,
            capability=capability,
            fact=_FACT,
            cause=IssueCause.FACT,
        )
    return CalculationIssue(
        code=AGREEMENT_UNMODELLED,
        message=(
            "a company or territorial agreement regulates the parental leave by "
            "the hour; the run applies the general criterion of art. 32 c. "
            "1-ter D.Lgs. 151/2001, not its rules"
        ),
        status=CalculationStatus.INCOMPLETE,
        capability=capability,
        cause=IssueCause.RULE,
    )
