"""The ferie of the Formazione professionale (Art. 43, p. 30).

"Il dipendente ha diritto ad un periodo annuale retribuito di ferie pari a 32
giorni lavorativi [...] Vengono riconosciute altresì 4 giornate di ferie in
sostituzione di tutte le festività soppresse", on a week "di 6 giorni
lavorativi"; "i periodi eccedenti i 15 giorni di calendario saranno
considerati mese intero".
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.leave.types import MonthCredit


def test_the_ferie_are_36_days_of_a_six_day_week() -> None:
    """32 days plus the 4 of the festività soppresse."""
    work = load_ccnl("formazione-professionale").work_rules
    assert work is not None
    rules = work.leave_rules
    assert rules is not None

    assert rules.default_annual_days == Decimal(36)
    assert [t.annual_days for t in rules.entitlement_tiers] == [Decimal(36)]
    assert rules.ferie_accrual is not None
    assert rules.ferie_accrual.month_credit is MonthCredit.MORE_THAN_HALF
