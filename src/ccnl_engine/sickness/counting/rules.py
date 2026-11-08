"""The comporto counting an employer chooses among those of its CCNL.

ABI Art. 66 c. 2: "I periodi di assenza per malattia e infortunio possono
essere calcolati dall'impresa con riferimento ai 48 mesi precedenti l'ultimo
giorno di assenza considerato", with periods of their own, in place of the
comporto of each illness of c. 1.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.comporto.models import ComportoBand

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

__all__ = ["with_window_counting"]


def with_window_counting(ccnl: CCNL, chosen: bool) -> CCNL:
    """Return the CCNL with the comporto counting the employer chose.

    The windows of ``SicknessRules.window_alternative`` replace the
    comporto windows, and their days the comporto of one illness, so that an
    illness never outlasts the window it is counted in.

    Returns:
        ``ccnl`` itself when the employer keeps the counting of each
        illness, else the CCNL with the alternative windows.

    Raises:
        InvalidInputError: When the employer chose a counting the CCNL does
            not offer.
    """
    if not chosen:
        return ccnl
    work = ccnl.work_rules
    rules = None if work is None else work.sickness_rules
    if work is None or rules is None or not rules.window_alternative:
        msg = (
            f"EmployerProfile.sickness_window_counting: {ccnl.meta.ccnl_id} offers "
            "no alternative comporto window"
        )
        raise InvalidInputError(
            msg, field="EmployerProfile.sickness_window_counting", feature="sickness"
        )
    windows = rules.window_alternative
    bands = tuple(
        ComportoBand(
            seniority_months_from=w.seniority_months_from,
            comporto_days=w.comporto_days,
            serious_comporto_days=w.serious_comporto_days,
            oncological_comporto_days=w.oncological_comporto_days,
        )
        for w in windows
    )
    sickness = rules.model_copy(
        update={"comporto_windows": windows, "comporto_bands": bands}
    )
    return ccnl.model_copy(
        update={"work_rules": work.model_copy(update={"sickness_rules": sickness})}
    )
