"""TFR rules: the Fondo di garanzia rate of the compensation by category.

INPS circ. 70/2007 par. 6: the Fondo di garanzia contribution is 0.20%,
0.40% for the dirigenti industriali.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.tax.severance.models import TfrCompensation

_COMPENSATION = TfrCompensation(
    guarantee_fund_rate=Decimal("0.0020"),
    guarantee_fund_rate_by_category={WorkerCategory.DIRIGENTE: Decimal("0.0040")},
    relief_rate=Decimal("0.0028"),
)


def test_category_rate_overrides_the_general_rate() -> None:
    """A dirigente takes 0.40%; an impiegato and an unknown category 0.20%."""
    assert _COMPENSATION.guarantee_fund_rate_for(WorkerCategory.DIRIGENTE) == Decimal(
        "0.0040"
    )
    assert _COMPENSATION.guarantee_fund_rate_for(WorkerCategory.IMPIEGATO) == Decimal(
        "0.0020"
    )
    assert _COMPENSATION.guarantee_fund_rate_for(None) == Decimal("0.0020")
