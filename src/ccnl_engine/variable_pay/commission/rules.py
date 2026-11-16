"""Pay the average of the commissions in an extra month of a commission level."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.errors import MissingRequiredFactError

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

__all__ = ["COMMISSION_AVERAGE", "with_commission_average"]

#: Code of the allowance that carries the commission average.
COMMISSION_AVERAGE = "commission_average"
_EXTRA_RUNS = frozenset({"thirteenth", "fourteenth"})


def with_commission_average(
    ccnl: CCNL, level_code: str, run_kind: str, average: Decimal | None
) -> CCNL:
    """Return the CCNL with the commission average in an extra month of the level.

    The extra month pays the twelfths of a monthly pay: the average joins
    the monthly pay of the level, so the same twelfths apply to it.

    Returns:
        ``ccnl`` unchanged on a regular run, for a level not paid by
        commission, or with an average of zero (a fixed-only operatore);
        else a copy whose level pays the average as a fixed allowance.

    Raises:
        MissingRequiredFactError: When an extra month of a commission level
            states no average.
    """
    rules = ccnl.work_rules
    commission = None if rules is None else rules.commission_levels
    if (
        run_kind not in _EXTRA_RUNS
        or commission is None
        or level_code not in commission.levels
    ):
        return ccnl
    if average is None:
        msg = (
            f"level {level_code} of {ccnl.meta.ccnl_id} is paid by commission: its "
            "extra months hold the monthly average of the commissions; state "
            "PeriodFacts.commission_average (0 for a fixed-only worker)"
        )
        raise MissingRequiredFactError(msg, feature="sales_commission")
    if not average:
        return ccnl
    added = Allowance(
        code=COMMISSION_AVERAGE,
        description="monthly average of the commissions of the year",
        monthly=TimeSeries(
            periods=(
                ValidityPeriod(valid_from=date.min, valid_until=None, value=average),
            )
        ),
        part_time_proportionable=False,
        apprenticeship_pct_relevant=False,
    )
    levels = tuple(
        level.model_copy(update={"fixed_allowances": (*level.fixed_allowances, added)})
        if level.code == level_code
        else level
        for level in ccnl.levels
    )
    return ccnl.model_copy(update={"levels": levels})
