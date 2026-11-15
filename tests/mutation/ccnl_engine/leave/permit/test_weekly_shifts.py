"""PAR hours that need a number of weekly shifts: Federmeccanica art. 5.

Renewal of 22 November 2025: 4 hours more from 1 January 2027 on 18 or more
weekly shifts with the night shift, 4 more from 1 January 2028 on 21, for
the workers not in the settore siderurgico.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.leave.permit.supplements import PermitExtraHours
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus, RuleProvenance

_RECORD = RuleProvenance(status=ProvenanceStatus.MISSING)
_EIGHTEEN = PermitExtraHours(
    hours=Decimal(4),
    valid_from=date(2027, 1, 1),
    excluded_subsectors=("steel",),
    min_weekly_shifts=18,
    provenance=_RECORD,
)
_DAY = date(2027, 3, 31)
#: A sub-sector other than the steel sector.
_OTHER = "general"


@pytest.mark.parametrize(
    ("day", "subsector", "shifts", "weekly", "applies", "unknown"),
    [
        (_DAY, _OTHER, True, 18, True, False),
        (_DAY, _OTHER, True, 17, False, False),
        (_DAY, _OTHER, True, None, False, True),
        (_DAY, _OTHER, None, None, False, True),
        (_DAY, _OTHER, False, None, False, False),
        (_DAY, None, True, 21, False, False),
        (_DAY, "steel", True, 21, False, False),
        (date(2026, 12, 31), _OTHER, True, 21, False, False),
    ],
)
def test_the_hours_need_the_weekly_shifts(
    day: date,
    subsector: str | None,
    shifts: bool | None,
    weekly: int | None,
    applies: bool,
    unknown: bool,
) -> None:
    """18 shifts or more from 2027, not the steel sector; unknown when unstated."""
    assert _EIGHTEEN.applies(day, subsector, shifts, weekly) is applies
    assert _EIGHTEEN.shift_fact_unknown(day, subsector, shifts, weekly) is unknown


def test_federmeccanica_grants_four_and_four_more() -> None:
    """104; 104 + 8 (15 shifts) + 4 on 18 shifts in 2027; + 4 more on 21 in 2028."""
    work = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert work is not None
    assert work.leave_rules is not None
    (permit,) = (p for p in work.leave_rules.permits if p.bucket == "rol")

    def hours(day: date, shifts: bool, weekly: int | None) -> Decimal:
        return permit.hours_for(
            50, None, _OTHER, day=day, qualifying_shifts=shifts, weekly_shifts=weekly
        )

    later = date(2028, 3, 31)
    assert hours(_DAY, False, None) == 104
    assert hours(_DAY, True, 18) == 116
    assert hours(later, True, 21) == 120
    assert hours(later, True, 18) == 116
